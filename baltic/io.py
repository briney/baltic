from io import BytesIO as csio
import json
import re
import requests
from typing import IO, Tuple, Union

from .dates import decimal_date
from .tree import Tree, make_tree, make_tree_json


def load_newick(
    tree_path: Union[str, IO],
    tip_regex: str = "\|([0-9]+\-[0-9]+\-[0-9]+)",
    date_fmt: str = "%Y-%m-%d",
    variable_date: bool = True,
    absolute_time: bool = False,
    verbose: bool = False,
    sort_branches: bool = True,
) -> Tree:
    """
    Load newick file
    """
    ll = None
    if isinstance(tree_path, str):
        handle = open(tree_path, "r")
    else:
        handle = tree_path

    for line in handle:
        l = line.strip("\n")
        if "(" in l:
            tree_string_start = l.index("(")
            ll = make_tree(l[tree_string_start:], verbose=verbose)
            if verbose:
                print("Identified tree string")

    assert ll, "Regular expression failed to find tree string"
    ll.traverse_tree(verbose=verbose)  ## traverse tree
    if sort_branches:
        ll.sort_branches()  ## traverses tree, sorts branches, draws tree

    if absolute_time:
        tip_dates = []
        tip_names = []
        for k in ll.get_external():
            n = k.name
            tip_names.append(n)
            cerberus = re.search(tip_regex, n)
            if cerberus is not None:
                tip_dates.append(
                    decimal_date(
                        cerberus.group(1), fmt=date_fmt, variable=variable_date
                    )
                )
        assert len(tip_dates) > 0, (
            "Regular expression failed to find tip dates in tip names, review regex pattern or set absolute_time option to False.\nFirst tip name encountered: %s\nDate regex set to: %s\nExpected date format: %s"
            % (tip_names[0], tip_regex, date_fmt)
        )
        highest_tip = max(tip_dates)
        ll.set_absolute_time(highest_tip)
    if isinstance(tree_path, str):
        handle.close()
    return ll


def load_nexus(
    tree_path: Union[str, IO],
    tip_regex: str = "\|([0-9]+\-[0-9]+\-[0-9]+)",
    date_fmt: str = "%Y-%m-%d",
    tree_string_regex: str = "tree [A-Za-z\_]+([0-9]+)",
    variable_date: bool = True,
    absolute_time: bool = True,
    verbose: bool = False,
    sort_branches: bool = True,
) -> Tree:
    """
    Load nexus file
    """
    tip_flag = False
    tips = {}
    tip_num = 0
    ll = None
    if isinstance(tree_path, str):
        handle = open(tree_path, "r")
    else:
        handle = tree_path

    for line in handle:
        l = line.strip("\n")

        cerberus = re.search("dimensions ntax=([0-9]+);", l.lower())
        if cerberus is not None:
            tip_num = int(cerberus.group(1))
            if verbose:
                print("File should contain %d taxa" % (tip_num))

        cerberus = re.search(tree_string_regex, l.lower())
        if cerberus is not None:
            tree_string_start = l.index("(")
            ll = make_tree(
                l[tree_string_start:]
            )  ## send tree string to make_tree function
            if verbose:
                print("Identified tree string")

        if tip_flag:
            cerberus = re.search("([0-9]+) ([A-Za-z\-\_\/\.'0-9 \|?]+)", l)
            if cerberus is not None:
                tips[cerberus.group(1)] = cerberus.group(2).strip('"').strip("'")
                if verbose:
                    print(
                        "Identified tip translation %s: %s"
                        % (cerberus.group(1), tips[cerberus.group(1)])
                    )
            elif ";" not in l:
                print("tip not captured by regex:", l.replace("\t", ""))

        if "translate" in l.lower():
            tip_flag = True
        if ";" in l:
            tip_flag = False

    assert ll, "Regular expression failed to find tree string"
    ll.traverse_tree()  ## traverse tree
    if sort_branches:
        ll.sort_branches()  ## traverses tree, sorts branches, draws tree
    if len(tips) > 0:
        ll.rename_tips(tips)  ## renames tips from numbers to actual names
        ll.tipMap = tips
    if absolute_time:
        tip_dates = []
        tip_names = []
        for k in ll.get_external():
            tip_names.append(k.name)
            cerberus = re.search(tip_regex, k.name)
            if cerberus is not None:
                tip_dates.append(
                    decimal_date(
                        cerberus.group(1), fmt=date_fmt, variable=variable_date
                    )
                )

        assert len(tip_dates) > 0, (
            "Regular expression failed to find tip dates in tip names, review regex pattern or set absolute_time option to False.\nFirst tip name encountered: %s\nDate regex set to: %s\nExpected date format: %s"
            % (tip_names[0], tip_regex, date_fmt)
        )
        highest_tip = max(tip_dates)
        ll.set_absolute_time(highest_tip)

    if isinstance(tree_path, str):
        handle.close()
    return ll


def load_json(
    json_object: Union[str, IO],
    json_translation: dict = {"name": "name", "absolute_time": "num_date"},
    verbose: bool = False,
    sort: bool = True,
    stats: bool = True,
) -> Tuple[Tree, dict]:
    """
    Load a nextstrain JSON by providing either the path to JSON or a file handle.
    json_translation is a dictionary that translates JSON attributes to baltic branch attributes (e.g. 'absolute_time' is called 'num_date' in nextstrain JSONs).
    Note that to avoid conflicts in setting node heights you can either define the absolute time of each node or branch lengths (e.g. if you want a substitution tree).
    """
    assert "name" in json_translation and (
        "absolute_time" in json_translation
        or "length" in json_translation
        or "height" in json_translation
    ), (
        "JSON translation dictionary missing entries: %s"
        % (
            ", ".join(
                [
                    entry
                    for entry in ["name", "height", "absolute_time", "length"]
                    if entry not in json_translation
                ]
            )
        )
    )
    if verbose:
        print("Reading JSON")

    if isinstance(json_object, str):
        ## string provided - either nextstrain URL or local path
        if "nextstrain.org" in json_object:  ## nextsrain.org in URL - request it
            if verbose:
                print("Assume URL provided, loading JSON from nextstrain.org")
            auspice_json = json.load(csio(requests.get(json_object).content))
        else:
            ## not nextstrain.org URL - assume local path to auspice v2 json
            if verbose:
                print("Loading JSON from local path")
            with open(json_object) as json_data:
                auspice_json = json.load(json_data)
    else:  #
        # not string, assume auspice v2 json object given
        if verbose:
            print("Loading JSON from object given")
        auspice_json = json_object

    json_meta = auspice_json["meta"]
    json_tree = auspice_json["tree"]
    ll = make_tree_json(json_tree, json_translation, verbose=verbose)

    assert (
        "absolute_time" in json_translation
        and ("length" not in json_translation or "height" not in json_translation)
    ) or (
        "absolute_time" not in json_translation
        and ("length" in json_translation or "height" in json_translation)
    ), "Cannot use both absolute time and branch length, include only one in json_translation dictionary."

    if verbose:
        print("Setting baltic traits from JSON")
    for k in ll.objects:
        ## make node attributes easier to access
        for key in k.traits["node_attrs"]:
            if isinstance(k.traits["node_attrs"][key], dict):
                if "value" in k.traits["node_attrs"][key]:
                    k.traits[key] = k.traits["node_attrs"][key]["value"]
                if "confidence" in k.traits["node_attrs"][key]:
                    k.traits[f"{key}_confidence"] = k.traits["node_attrs"][key][
                        "confidence"
                    ]
            elif key == "div":
                k.traits["divergence"] = k.traits["node_attrs"][key]

    for attr in json_translation:
        for k in ll.objects:
            if isinstance(json_translation[attr], str):
                if json_translation[attr] in k.traits:
                    ## set attribute value for branch
                    setattr(k, attr, k.traits[json_translation[attr]])
                elif (
                    "node_attrs" in k.traits
                    and json_translation[attr] in k.traits["node_attrs"]
                ):
                    setattr(k, attr, k.traits["node_attrs"][json_translation[attr]])
                elif (
                    "branch_attrs" in k.traits
                    and json_translation[attr] in k.traits["branch_attrs"]
                ):
                    setattr(k, attr, k.traits["branch_attrs"][json_translation[attr]])
                else:
                    raise KeyError(
                        f"String attribute {json_translation[attr]} not found in JSON"
                    )
            elif callable(json_translation[attr]):
                ## set attribute value with a function for branch
                setattr(k, attr, json_translation[attr](k))
            else:
                raise AttributeError(
                    f"Attribute {json_translation[attr]} neither string nor callable"
                )

    ## iterate between divergence and absolute time
    for branch_unit in ["height", "absolute_time"]:
        if branch_unit in json_translation:  ## it's available in tree
            for k in ll.objects:
                cur_branch = getattr(k, branch_unit)  ## get parameter for this branch
                ## get parameter for parental branch
                par_branch = getattr(k.parent, branch_unit)
                # difference between current and parent is branch length
                # (or, if parent unavailabel it's 0)
                k.length = cur_branch - par_branch if cur_branch and par_branch else 0.0

    if verbose:
        print("Traversing and drawing tree")

    ll.traverse_tree(verbose=verbose)
    ll.draw_tree()
    if stats:
        ll.tree_stats()  ## initial traversal, checks for stats
    if sort:
        ll.sort_branches()  ## traverses tree, sorts branches, draws tree

    cmap = {}
    for colouring in json_meta["colorings"]:
        if colouring["type"] == "categorical" and "scale" in colouring:
            cmap[colouring["key"]] = {}
            for entry in colouring["scale"]:
                key, value = entry
                cmap[colouring["key"]][key] = value
    setattr(ll, "cmap", cmap)

    return ll, json_meta


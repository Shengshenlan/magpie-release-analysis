#!/usr/bin/env python3
"""Turn fetched release pages into ordered (prev, tag) pairs by version."""
import glob, sys


def load_tags():
    tags = set()
    for f in glob.glob("/tmp/magpie_data/pages/*.tsv"):
        for line in open(f):
            tag = line.split("\t")[0].strip()
            if tag.startswith("v0.1."):
                tags.add(tag)
    def key(t):
        try:
            return int(t.split(".")[-1])
        except ValueError:
            return -1
    return sorted(tags, key=key)


def main():
    tags = load_tags()
    for prev, cur in zip(tags, tags[1:]):
        print(f"{prev} {cur}")


if __name__ == "__main__":
    main()

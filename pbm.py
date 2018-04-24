"""Executes various steps within the PubMed Best Match (pbm) pipeline.

Usage:
    pbm load
    pbm classify
    pbm fetch
    pbm calculate
    pbm train
    pbm evaluate (before|after)
"""
from docopt import docopt

# TODO: add controls to verify the workflow (e.g. not to train before loading articles)
def main():
    args = docopt(__doc__)
    if args["load"]:
        from bestmatch import loadData
    if args["classify"]:
        from bestmatch import classifyQueries
    if args["fetch"]:
        from bestmatch import fetchArticles
    if args["calculate"]:
        from bestmatch import createDataset
    if args["train"]:
        from bestmatch import train
    if args["evaluate"]:
        from bestmatch import evaluate
        if args["before"]:
            evaluate.evaluate(False)
        if args["after"]:
            evaluate.evaluate(True)

if __name__ == '__main__':
    main()

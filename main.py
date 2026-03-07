import argparse
import subprocess


def main():
    p = argparse.ArgumentParser(prog="igrep")
    p.add_argument("query_or_cmd", nargs="?", help="Pattern/text or sync/setup")
    p.add_argument("topk", nargs="?", type=int, help="Top-k for semantic search (-s)")
    p.add_argument("-i", "--ignore-case", action="store_true", help="Ignore case")
    p.add_argument("-c", "--count", action="store_true", help="Count occurrences")
    p.add_argument("-s", "--semantic", action="store_true", help="Semantic search")
    args = p.parse_args()

    q = (args.query_or_cmd or "").strip()
    if args.query_or_cmd == "sync":
        from src.connector.sync import sync_data
        sync_data()
        return
    if args.query_or_cmd == "setup":
        print("Setting up the application.")
        subprocess.run(["uv", "run", "setup.py"])
        return
    if args.semantic:
        from src.connector.semantic import semantic_search
        semantic_search(q, top_k=args.topk or 5)
        return
    if not q:
        p.error("query_or_cmd required for search")
    from src.connector.pattern import search_e, search_i, search_c
    if args.count:
        search_c(q)
    elif args.ignore_case:
        search_i(q)
    else:
        search_e(q)


if __name__ == "__main__":
    main()

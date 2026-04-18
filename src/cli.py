import argparse


def main() -> None:
    p = argparse.ArgumentParser(prog="igrep")
    p.add_argument("query_or_cmd", nargs="?", help="Pattern/text or sync/setup/track")
    p.add_argument("topk", nargs="?", type=int, help="Top-k results (pattern) or semantic search")
    p.add_argument("-i", "--ignore-case", action="store_true", help="Ignore case")
    p.add_argument("-c", "--count", action="store_true", help="Count occurrences")
    p.add_argument("-s", "--semantic", action="store_true", help="Semantic search")
    p.add_argument("--track", action="store_true", help="Manage tracked folders")
    args = p.parse_args()

    q = (args.query_or_cmd or "").strip()
    limit = args.topk or 5

    # --track
    if args.track:
        from src.lib.path_manager import add_path, list_paths
        if q:
            add_path(q)
        else:
            paths = list_paths()
            if not paths:
                print('No tracked folders yet. Use: igrep --track "C:\\path\\to\\folder"')
            else:
                print("Tracked folders:")
                for i, path in enumerate(paths, 1):
                    print(f"  {i}. {path}")
        return

    if args.query_or_cmd == "sync":
        from src.connector.sync import sync_data
        sync_data()
        return

    if args.query_or_cmd == "setup":
        from setup_cmd import setup
        setup()
        return

    if args.semantic:
        from src.connector.semantic import semantic_search
        semantic_search(q, top_k=limit)
        return

    if not q:
        p.error("query_or_cmd required for search")

    from src.connector.pattern import search_e, search_i, search_c
    if args.count:
        search_c(q)
    elif args.ignore_case:
        search_i(q, limit=limit)
    else:
        search_e(q, limit=limit)

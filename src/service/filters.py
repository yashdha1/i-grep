import dataclasses


@dataclasses.dataclass
class FilteredRow:
    index: int
    location: str
    context: str  # only the line where the query matches, not full text

    def __str__(self) -> str:
        return f"{self.location} | {self.context}"


def filter_rows(rows, query) :
    filtered_rows = []
    query_words = query.split()
    for row in rows:
        index = row[0]
        location = row[1]
        full_context = row[2]

        matching_line = None
        for line in full_context.splitlines():
            line_stripped = line.strip()
            if not line_stripped:
                continue
            for word in query_words:
                if word in line_stripped:
                    matching_line = line_stripped
                    break
            if matching_line is not None:
                break

        if matching_line is not None:
            filtered_rows.append(FilteredRow(index=index, location=location, context=matching_line))
    return filtered_rows
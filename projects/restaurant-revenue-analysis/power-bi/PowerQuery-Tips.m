let
    Source = Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/ashutoshmahanta714-bit/ashutoshmahanta714-bit/main/projects/restaurant-revenue-analysis/data/tips.csv"),
        [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"total_bill", type number}, {"tip", type number},
        {"sex", type text}, {"smoker", type text}, {"day", type text},
        {"time", type text}, {"size", Int64.Type}
    }, "en-US"),
    ValidRows = Table.SelectRows(Typed, each [total_bill] > 0 and [tip] >= 0 and [size] > 0),
    Renamed = Table.RenameColumns(ValidRows, {
        {"total_bill", "Total Bill"}, {"tip", "Tip"},
        {"sex", "Server Sex"}, {"smoker", "Smoker"},
        {"day", "Day"}, {"time", "Meal"}, {"size", "Party Size"}
    }),
    DayOrder = Table.AddColumn(Renamed, "Day Sort", each
        if [Day] = "Thur" then 1 else if [Day] = "Fri" then 2
        else if [Day] = "Sat" then 3 else 4, Int64.Type)
in
    DayOrder

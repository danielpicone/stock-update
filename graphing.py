# Creating the portfolio charts

def graph_indiv_stock(file_name = "portfolio_charts.pdf"):
    # import matplotlib.pyplot as plt
    # import matplotlib.gridspec as gridspec
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.dates as mdates

    def format_date(x, pos = None):
        thisind = np.clip(int(x + 0.5), 0, N -1)
        return entire_df["date"][thisind].strftime("%Y-%m-%d")

    df = get_price_history_df(start_date = "2019-01-01")
    min_df = get_min_date(df)
    portfolio_df = df.merge(min_df[["name","value", "price"]]\
    .rename(columns={"value": "start_value", "price":"start_price"}),
        how = "left", on = "name")
    portfolio_df["stock_return"] = portfolio_df.apply(lambda row: row["price"]/row["start_price"], axis=1)
    portfolio_df = portfolio_df.merge(portfolio_df.groupby("date", as_index=False)\
        .agg({"value":"sum"}).rename(columns={"value":"portfolio_value"}),
        how = "left", on = "date")
    portfolio_df["proportion"] = portfolio_df.apply(lambda row: row["value"]/row["portfolio_value"], axis=1)
    portfolio_df["return_proportion"] = portfolio_df.apply(lambda row: row["stock_return"]*row["proportion"], axis=1)
    names = portfolio_df["name"].unique()

    with PdfPages(file_name) as pdf:
        entire_df = portfolio_df.groupby("date", as_index = False).agg({"return_proportion":"sum"})
        plt.figure(tight_layout = True)
        N = len(entire_df.date)
        plt.plot(range(len(entire_df.date)), entire_df["return_proportion"].tolist(), "-")
        plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
        plot_formatter(plt)
        plt.title("Return of total portfolio")
        pdf.savefig()
        plt.close()
        for (i, s) in enumerate(names):
            plt.figure(tight_layout = True)
            gs = gridspec.GridSpec(len(names), 1)
            stock_df = portfolio_df[portfolio_df["name"]==s]
            N = len(stock_df.date)
            x_axis = range(len(stock_df["date"]))
            plt.plot(x_axis, stock_df["stock_return"].tolist(), "-")
            plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
            plt.gca().set_ylim(0.95*portfolio_df["stock_return"].min(),
                1.05*portfolio_df["stock_return"].max())
            plot_formatter(plt)
            plt.title("Return of " + s)
            pdf.savefig()
            plt.close()


def plot_formatter(plot):
    years = mdates.YearLocator()
    months = mdates.MonthLocator()
    days = mdates.DayLocator()
    plt.grid(True)

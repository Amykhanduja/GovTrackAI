class ChartEngine:
    def __init__(self, workbook):
        self.workbook = workbook

    def create_chart(self, chart_type, title, sheet_name, cats, vals):
        chart = self.workbook.add_chart({'type': chart_type})
        series_dict = {
            'name': title,
            'categories': [sheet_name, *cats],
            'values':     [sheet_name, *vals]
        }
        if chart_type == 'pie':
            series_dict['data_labels'] = {'percentage': True}
            
        chart.add_series(series_dict)
        chart.set_title({'name': title})
        chart.set_legend({'position': 'bottom'})
        
        # Power BI clean aesthetics (no borders on chart area)
        chart.set_chartarea({'border': {'none': True}})
        return chart

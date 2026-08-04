import logging
import xlsxwriter
import os
from datetime import datetime
from excel.data_provider import DataProvider
from excel.formatter import FormattingEngine
from excel.charts import ChartEngine

logger = logging.getLogger('app.excel.engine')

class ExcelEngine:
    def __init__(self, config, db_manager=None):
        self.output_dir = config.get('output_dir', 'downloads/reports')
        os.makedirs(self.output_dir, exist_ok=True)
        self.file_path = os.path.join(self.output_dir, 'GovTrack_Master_Dashboard.xlsx')
        self.data_provider = DataProvider(db_manager)

    def generate(self):
        logger.info(f"Generating BI Dashboard at {self.file_path}")
        workbook = xlsxwriter.Workbook(self.file_path, {'strings_to_urls': False})
        
        self.formatter = FormattingEngine(workbook)
        self.chart_engine = ChartEngine(workbook)
        
        self._build_chart_data_sheet(workbook)
        self._build_dashboard_sheet(workbook)
        self._build_master_jobs_sheet(workbook)
        self._build_applications_sheet(workbook)
        self._build_exams_sheet(workbook)
        
        workbook.close()
        logger.info("Workbook BI generation complete.")

    def _build_dashboard_sheet(self, workbook):
        sheet = workbook.add_worksheet("Dashboard")
        sheet.set_tab_color('#0078D4')
        sheet.hide_gridlines(2)
        sheet.set_column('A:Z', 15)
        
        # Title
        title_fmt = workbook.add_format({'bold': True, 'font_size': 24, 'font_color': '#252423'})
        sheet.write('B2', 'GovTrack AI Executive Dashboard', title_fmt)
        sheet.write('B3', f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # KPI Cards (2 rows of 5)
        kpis = list(self.data_provider.get_dashboard_kpis().items())
        start_row, start_col = 4, 1
        
        for i, (title, val) in enumerate(kpis[:10]):
            r = start_row + (i // 5) * 3
            c = start_col + (i % 5) * 2
            sheet.write(r, c, title, self.formatter.kpi_title)
            sheet.write(r+1, c, val, self.formatter.kpi_value)
            
        # Insert Charts
        pie1 = self.chart_engine.create_chart('pie', 'Application Status', 'ChartData', [1,0,3,0], [1,1,3,1])
        sheet.insert_chart('B11', pie1, {'x_scale': 1.2, 'y_scale': 1.2})
        
        pie2 = self.chart_engine.create_chart('pie', 'Top Organizations', 'ChartData', [5,0,8,0], [5,1,8,1])
        sheet.insert_chart('G11', pie2, {'x_scale': 1.2, 'y_scale': 1.2})

        col1 = self.chart_engine.create_chart('column', 'Recruitment Trend', 'ChartData', [10,0,15,0], [10,1,15,1])
        sheet.insert_chart('B29', col1, {'x_scale': 2.5, 'y_scale': 1.2})

    def _build_master_jobs_sheet(self, workbook):
        sheet = workbook.add_worksheet("Master Jobs")
        sheet.set_tab_color('#107C10')
        sheet.freeze_panes(1, 0)
        
        jobs = self.data_provider.get_master_jobs()
        headers = [{'header': 'ID'}, {'header': 'Organization'}, {'header': 'Post'}, 
                   {'header': 'Priority'}, {'header': 'Status'}, {'header': 'Salary'}, 
                   {'header': 'Deadline'}, {'header': 'Official Link'}]
                   
        data = []
        for job in jobs:
            data.append([job['id'], job['org'], job['post'], job['priority'], job['status'], job['salary'], job['deadline'], job['link']])
            
        sheet.add_table(0, 0, len(jobs), len(headers)-1, {
            'data': data,
            'columns': headers,
            'style': 'Table Style Light 9'
        })
        
        sheet.set_column('A:A', 5)
        sheet.set_column('B:C', 20)
        sheet.set_column('D:E', 12)
        sheet.set_column('F:F', 15, self.formatter.currency)
        sheet.set_column('G:H', 20)
        
        # Hyperlinks for column H
        for i, job in enumerate(jobs, 1):
            sheet.write_url(i, 7, job['link'], self.formatter.hyperlink, string="Apply Here")
            
        self.formatter.apply_traffic_lights(sheet, f'E2:E{len(jobs)+1}')

    def _build_applications_sheet(self, workbook):
        sheet = workbook.add_worksheet("Applications")
        sheet.set_tab_color('#D13438')
        
        apps = self.data_provider.get_applications()
        headers = [{'header': 'App ID'}, {'header': 'Org'}, {'header': 'Post'}, 
                   {'header': 'Date'}, {'header': 'Fee'}, {'header': 'Status'}, {'header': 'Progress'}]
                   
        data = [[a['app_id'], a['org'], a['post'], a['date'], a['fee'], a['status'], a['progress']] for a in apps]
            
        sheet.add_table(0, 0, len(apps), len(headers)-1, {
            'data': data,
            'columns': headers,
            'style': 'Table Style Medium 2'
        })
        sheet.set_column('A:F', 18)
        sheet.set_column('G:G', 15, self.formatter.percent)
        
        # Data bars for progress
        sheet.conditional_format(f'G2:G{len(apps)+1}', {'type': 'data_bar', 'bar_color': '#63C384'})

    def _build_exams_sheet(self, workbook):
        sheet = workbook.add_worksheet("Exam Calendar")
        sheet.set_tab_color('#FFB900')
        
        exams = self.data_provider.get_exams()
        headers = [{'header': 'Org'}, {'header': 'Exam'}, {'header': 'Date'}, {'header': 'Status'}]
        data = [[e['org'], e['exam'], e['date'], e['status']] for e in exams]
        
        sheet.add_table(0, 0, len(exams), len(headers)-1, {
            'data': data,
            'columns': headers,
            'style': 'Table Style Medium 5'
        })
        sheet.set_column('A:D', 20)

    def _build_chart_data_sheet(self, workbook):
        sheet = workbook.add_worksheet("ChartData")
        sheet.hide()
        data = self.data_provider.get_chart_data()
        
        def write_dict(start_row, title, d):
            sheet.write(start_row, 0, title)
            sheet.write(start_row, 1, 'Value')
            r = start_row + 1
            for k, v in d.items():
                sheet.write(r, 0, k)
                sheet.write(r, 1, v)
                r += 1
            return r + 1
            
        r = write_dict(0, 'Status', data['status_dist'])
        r = write_dict(r, 'Org', data['org_dist'])
        write_dict(r, 'Month', data['monthly_trend'])

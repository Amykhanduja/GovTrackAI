class FormattingEngine:
    def __init__(self, workbook):
        self.workbook = workbook
        self._init_formats()

    def _init_formats(self):
        # Power BI Theme Colors
        self.theme = {
            'bg': '#F3F2F1', 'card_bg': '#FFFFFF', 
            'text_dark': '#252423', 'text_light': '#605E5C',
            'primary': '#0078D4', 'accent': '#107C10',
            'red': '#D13438', 'yellow': '#FFB900'
        }

        self.kpi_title = self.workbook.add_format({
            'bold': True, 'font_size': 11, 'font_color': self.theme['text_light'],
            'bg_color': self.theme['card_bg'], 'align': 'center', 'valign': 'vcenter',
            'top': 1, 'left': 1, 'right': 1
        })
        self.kpi_value = self.workbook.add_format({
            'bold': True, 'font_size': 20, 'font_color': self.theme['primary'],
            'bg_color': self.theme['card_bg'], 'align': 'center', 'valign': 'vcenter',
            'bottom': 1, 'left': 1, 'right': 1
        })

        self.header_fmt = self.workbook.add_format({
            'bold': True, 'bg_color': self.theme['primary'], 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })

        self.currency = self.workbook.add_format({'num_format': '₹ #,##0'})
        self.percent = self.workbook.add_format({'num_format': '0%'})
        self.hyperlink = self.workbook.add_format({'font_color': 'blue', 'underline': 1})
        
        # Traffic lights
        self.status_green = self.workbook.add_format({'bg_color': '#DFF6DD', 'font_color': '#107C10'})
        self.status_red = self.workbook.add_format({'bg_color': '#FDE7E9', 'font_color': '#D13438'})
        self.status_yellow = self.workbook.add_format({'bg_color': '#FFF4CE', 'font_color': '#795804'})

    def apply_traffic_lights(self, worksheet, range_str):
        worksheet.conditional_format(range_str, {'type': 'cell', 'criteria': '==', 'value': '"Applied"', 'format': self.status_green})
        worksheet.conditional_format(range_str, {'type': 'cell', 'criteria': '==', 'value': '"Urgent"', 'format': self.status_red})
        worksheet.conditional_format(range_str, {'type': 'cell', 'criteria': '==', 'value': '"New"', 'format': self.status_yellow})

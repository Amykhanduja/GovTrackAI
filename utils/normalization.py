class NormalizationEngine:
    def normalize(self, org_id: str, raw_data: dict) -> dict:
        # Ensure all fields are present and standardized
        return {
            'org_id': org_id,
            'title': raw_data.get('title', 'Unknown Title'),
            'department': raw_data.get('department', ''),
            'post_name': raw_data.get('post_name', ''),
            'salary': raw_data.get('salary', ''),
            'qualification': raw_data.get('qualification', ''),
            'age_limit': raw_data.get('age_limit', ''),
            'experience': raw_data.get('experience', ''),
            'notification_url': raw_data.get('notification_url', ''),
            'application_link': raw_data.get('application_link', ''),
            'important_dates': raw_data.get('important_dates', {}),
            'status': raw_data.get('status', 'Active'),
            'document_links': raw_data.get('document_links', [])
        }

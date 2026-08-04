# Personal Career Assistant

## Overview
GovTrack AI Phase 7 upgrades the recruitment tracker into a fully personalized **Career Management Engine**.

## Architecture
- **`UserProfileManager`**: Stores Education, Skills, and Preferences in a central config.
- **`SmartSearchEngine`**: Natural language routing for job queries (e.g. "Cyber jobs > 10 LPA").
- **`ApplicationTracker`**: Strict lifecycle management (Submitted -> Fee Paid -> Admit Card -> Interview -> Offer).
- **`CareerWorkspace`**: Tags, Favorites, Watchlists, Timelines, Bookmarks.
- **`DocumentRepository`**: Vault for Resumes, Identity Docs, Receipts.
- **`CareerAnalytics`**: Calculates Skill Gaps by diffing User Profile against scraped Market Demand data.

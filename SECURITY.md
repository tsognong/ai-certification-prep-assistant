# Security & Privacy Features

## Session-Based Rate Limiting

This application implements secure session tracking to ensure fair usage of AI resources and prevent abuse.

### Implementation Details

**Session Identification**:
- Uses browser characteristics for unique session identification
- Implements localStorage persistence for session continuity
- SHA-256 hashing ensures privacy protection
- No personally identifiable information (PII) is collected

**Rate Limiting**:
- Maximum 5 quiz attempts per configuration per session
- Attempts are tracked by session ID, not nickname
- Prevents API abuse and ensures equitable access

**Privacy Protection**:
- Only cryptographic hashes are stored in the database
- Original session identifiers are never persisted
- No tracking of browsing behavior outside the app
- Complies with privacy best practices

### Error Handling

**User-Facing Errors**:
- Generic error messages prevent information disclosure
- Stack traces are hidden from users
- No exposure of credentials or sensitive configuration
- Graceful degradation when services are unavailable

**Security Benefits**:
- ✅ Prevents API cost abuse
- ✅ Ensures fair resource allocation
- ✅ Privacy-preserving identification
- ✅ No credential exposure in error messages
- ✅ Transparent session tracking (users can see their limits)

### Technical Stack

- **AI Generation**: Google Gemini API
- **Database**: MongoDB Atlas
- **Session Management**: Browser-based with localStorage
- **Security**: SHA-256 cryptographic hashing

### Configuration

Maximum retakes per quiz: **5 attempts**

To modify this limit, update the `MAX_RETAKES` constant in `app.py`:
```python
MAX_RETAKES = 5  # Change this value as needed
```

### Notes for Developers

- Error messages are deliberately generic to prevent information leakage
- Database connection errors do not expose MongoDB URIs
- API errors do not reveal API keys or request details
- Session tracking implementation details are abstracted from users

# text_cleaner.py
import re
from typing import Dict, List, Tuple

class TextCleaner:
    def __init__(self):
        # Patterns for both English and Bahasa Indonesia
        self.header_patterns = [
            r'^BAB\s+\d+',  # "BAB 1" - Chapter in Indonesian
            r'^CHAPTER\s+\d+',
            r'^\d+\.\s+[A-Z][A-Za-z\s]+$',
            r'^[A-Z][A-Z\s]{3,}$',  # ALL CAPS HEADERS
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]+){2,}$'  # Title Case Headers (3+ words)
        ]
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove multiple spaces first
        text = re.sub(r' {2,}', ' ', text)
        
        # Fix hyphenated words at line breaks
        text = re.sub(r'-\n', '', text)
        
        # Remove page numbers (just a number on its own line)
        text = re.sub(r'\n\d{1,3}\n', '\n', text)
        
        # Strip each line and rejoin
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove empty lines (this is the key fix!)
        lines = [line for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        # Now add back paragraph breaks (double newline) where appropriate
        # Replace single newlines with space, except before headers
        final_lines = []
        for i, line in enumerate(text.split('\n')):
            if i == 0:
                final_lines.append(line)
                continue
            
            # Check if current line is a header
            is_header = any(re.match(pattern, line.strip()) for pattern in self.header_patterns)
            prev_line = text.split('\n')[i-1] if i > 0 else ""
            prev_is_header = any(re.match(pattern, prev_line.strip()) for pattern in self.header_patterns)
            
            # Add paragraph break before headers or after headers
            if is_header or prev_is_header:
                final_lines.append('')  # Empty line for paragraph break
                final_lines.append(line)
            else:
                # Continue same paragraph
                if final_lines:
                    final_lines[-1] += ' ' + line
                else:
                    final_lines.append(line)
        
        return '\n\n'.join([l for l in final_lines if l.strip()])
    
    def identify_headers(self, text: str) -> List[Tuple[int, str]]:
        """Identify likely section headers."""
        lines = text.split('\n')
        headers = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            for pattern in self.header_patterns:
                if re.match(pattern, line_stripped):
                    headers.append((i, line_stripped))
                    break
        
        return headers
    
    def split_into_sections(self, text: str) -> List[Dict]:
        """Split text into sections based on headers."""
        headers = self.identify_headers(text)
        lines = [l for l in text.split('\n') if l.strip()]  # Remove empty lines
        
        if not headers:
            # No headers found, treat whole text as one section
            return [{
                "header": "Content",
                "content": text,
                "start_line": 0
            }]
        
        sections = []
        
        for i, (line_num, header) in enumerate(headers):
            # Find actual position in cleaned lines
            header_pos = None
            for idx, line in enumerate(lines):
                if line.strip() == header:
                    header_pos = idx
                    break
            
            if header_pos is None:
                continue
            
            # Get content between this header and next header
            start = header_pos + 1
            
            # Find next header position
            if i + 1 < len(headers):
                next_header = headers[i + 1][1]
                end = None
                for idx, line in enumerate(lines[start:], start=start):
                    if line.strip() == next_header:
                        end = idx
                        break
                if end is None:
                    end = len(lines)
            else:
                end = len(lines)
            
            content = '\n'.join(lines[start:end])
            
            sections.append({
                "header": header,
                "content": content.strip(),
                "start_line": header_pos
            })
        
        return sections
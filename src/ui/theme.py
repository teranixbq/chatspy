"""Aura color theme for Textual UI."""

from textual.design import ColorSystem


# Aura color palette
AURA_COLORS = {
    # Primary colors
    "primary": "#a277ff",  # Purple
    "secondary": "#61ffca",  # Cyan
    "accent": "#ffca85",  # Orange
    
    # Background colors
    "background": "#15141b",  # Dark background
    "surface": "#1d1c26",  # Slightly lighter surface
    "surface-variant": "#252332",  # Even lighter variant
    
    # Text colors
    "text": "#edecee",  # Light gray text
    "text-muted": "#6d6d6d",  # Muted gray
    "text-disabled": "#3d3d3d",  # Disabled gray
    
    # Status colors
    "success": "#29d398",  # Green
    "warning": "#ffca85",  # Orange
    "error": "#ff6767",  # Red
    "info": "#61ffca",  # Cyan
    
    # UI element colors
    "border": "#3d3d3d",
    "border-focused": "#a277ff",
    "selection": "#a277ff40",  # Purple with alpha
}


def get_aura_theme() -> str:
    """Get Aura theme as Textual CSS.
    
    Returns:
        CSS string for Aura theme
    """
    return f"""
/* Aura Theme for ChatSpy */

Screen {{
    background: {AURA_COLORS['background']};
}}

/* Containers */
Container {{
    background: {AURA_COLORS['surface']};
    border: solid {AURA_COLORS['border']};
}}

Container:focus {{
    border: solid {AURA_COLORS['border-focused']};
}}

/* Text & Labels */
Label {{
    color: {AURA_COLORS['text']};
}}

Static {{
    color: {AURA_COLORS['text']};
}}

/* Input */
Input {{
    background: {AURA_COLORS['surface-variant']};
    color: {AURA_COLORS['text']};
    border: solid {AURA_COLORS['border']};
}}

Input:focus {{
    border: solid {AURA_COLORS['border-focused']};
}}

Input.-invalid {{
    border: solid {AURA_COLORS['error']};
}}

/* Buttons */
Button {{
    background: {AURA_COLORS['primary']};
    color: {AURA_COLORS['background']};
    border: none;
}}

Button:hover {{
    background: #b38aff;
}}

Button:focus {{
    background: {AURA_COLORS['primary']};
    border: solid {AURA_COLORS['border-focused']};
}}

Button.-primary {{
    background: {AURA_COLORS['primary']};
}}

Button.-success {{
    background: {AURA_COLORS['success']};
}}

Button.-warning {{
    background: {AURA_COLORS['warning']};
}}

Button.-error {{
    background: {AURA_COLORS['error']};
}}

/* Lists */
ListView {{
    background: {AURA_COLORS['surface']};
    color: {AURA_COLORS['text']};
    border: solid {AURA_COLORS['border']};
}}

ListItem {{
    background: {AURA_COLORS['surface']};
    color: {AURA_COLORS['text']};
}}

ListItem:hover {{
    background: {AURA_COLORS['surface-variant']};
}}

ListItem.-selected {{
    background: {AURA_COLORS['selection']};
    color: {AURA_COLORS['primary']};
}}

/* Header & Footer */
Header {{
    background: {AURA_COLORS['surface-variant']};
    color: {AURA_COLORS['primary']};
}}

Footer {{
    background: {AURA_COLORS['surface-variant']};
    color: {AURA_COLORS['text-muted']};
}}

/* Scrollbars */
Scrollbar {{
    background: {AURA_COLORS['surface']};
}}

Scrollbar:hover {{
    background: {AURA_COLORS['surface-variant']};
}}

/* Status indicators */
.status-online {{
    color: {AURA_COLORS['success']};
}}

.status-offline {{
    color: {AURA_COLORS['text-muted']};
}}

.status-error {{
    color: {AURA_COLORS['error']};
}}

/* Message styles */
.message-sender {{
    color: {AURA_COLORS['primary']};
}}

.message-content {{
    color: {AURA_COLORS['text']};
}}

.message-timestamp {{
    color: {AURA_COLORS['text-muted']};
}}

/* System messages */
.system-message {{
    color: {AURA_COLORS['info']};
    text-style: italic;
}}

.error-message {{
    color: {AURA_COLORS['error']};
}}

.warning-message {{
    color: {AURA_COLORS['warning']};
}}
"""

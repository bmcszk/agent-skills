# Tools Reference

Load when invoking browser (@pw) or image-analysis (@minimax) tools via mcpc.

## Tools Reference

### Navigation (mcpc @pw)
| Command | Use |
|---------|-----|
| `mcpc @pw tools-call browser_navigate url:=<url>` | Go to URL |
| `mcpc @pw tools-call browser_navigate_back` | Go back |
| `mcpc @pw tools-call browser_close` | Close browser |
| `mcpc @pw tools-call browser_resize width:=1280 height:=720` | Resize window |
| `mcpc @pw tools-call browser_tabs action:="open"` | Manage tabs |

### Interaction (mcpc @pw)
| Command | Use |
|---------|-----|
| `mcpc @pw tools-call browser_click target:=<ref>` | Click element (use ref from snapshot) |
| `mcpc @pw tools-call browser_type target:=<ref> text:=<text>` | Type text |
| `mcpc @pw tools-call browser_press_key key:="Enter"` | Press key |
| `mcpc @pw tools-call browser_hover target:=<ref>` | Hover element |
| `mcpc @pw tools-call browser_drag startTarget:=<ref> endTarget:=<ref>` | Drag and drop |
| `mcpc @pw tools-call browser_select_option target:=<ref> values:='["val"]'` | Select dropdown |
| `mcpc @pw tools-call browser_fill_form fields:='[...]'` | Fill multiple fields |
| `mcpc @pw tools-call browser_file_upload paths:='["/path"]'` | Upload files |
| `mcpc @pw tools-call browser_handle_dialog accept:=true` | Handle alerts |

### Verification (mcpc @pw)
| Command | Use |
|---------|-----|
| `mcpc @pw tools-call browser_snapshot` | **Get page structure (USE FIRST)** |
| `mcpc @pw tools-call browser_take_screenshot` | **Capture visual (REQUIRED)** |
| `mcpc @pw tools-call browser_wait_for text:=<text>` | Wait for text/element |
| `mcpc @pw tools-call browser_console_messages` | Get console logs |
| `mcpc @pw tools-call browser_network_requests` | Get network logs |
| `mcpc @pw tools-call browser_evaluate function:=<js>` | Run JavaScript |

### AI Analysis (mcpc @minimax)
| Command | Use |
|---------|-----|
| `mcpc @minimax tools-call understand_image prompt:=<prompt> image_source:=<path>` | Analyze screenshots with AI |
| `mcpc @minimax tools-call web_search query:=<query>` | Search web for info |


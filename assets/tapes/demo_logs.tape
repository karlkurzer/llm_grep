# Demo 1: Log Analysis - Extract errors and warnings from noisy logs
Output assets/demo_logs.gif

Set Shell "bash"
Set FontSize 20
Set Width 1300
Set Height 620
Set Theme "Catppuccin Mocha"
Set WindowBar Colorful
Set Padding 20
Set Margin 10
Set MarginFill "#1e1e2e"
Set BorderRadius 8
Set TypingSpeed 50ms
Set Framerate 30
Set PlaybackSpeed 1
Set CursorBlink false

# Hidden setup: create llm_grep function that fakes streaming output
Hide
Type `llm_grep() { cat > /dev/null; while IFS= read -r line; do echo "$line"; sleep 0.3; done < assets/fake_data/output_logs.txt; }`
Enter
Sleep 500ms
Type "export PS1='$ '"
Enter
Sleep 300ms
Type "clear"
Enter
Sleep 500ms
Show

# Visible: show the log file first (briefly)
Sleep 500ms
Type "cat assets/fake_data/sample_logs.txt | llm_grep "
Sleep 300ms
Type@30ms `"show only error and warning lines"`
Sleep 1s
Enter
Sleep 5s
Sleep 2s

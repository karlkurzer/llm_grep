# Demo 3: Process Analysis - Find top memory consumers
Output assets/demo_process.gif

Set Shell "bash"
Set FontSize 20
Set Width 1300
Set Height 550
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

# Hidden setup
Hide
Type `llm_grep() { cat > /dev/null; while IFS= read -r line; do echo "$line"; sleep 0.2; done < assets/fake_data/output_ps.txt; }`
Enter
Sleep 500ms
Type "export PS1='$ '"
Enter
Sleep 300ms
Type "clear"
Enter
Sleep 500ms
Show

# Visible demo
Sleep 500ms
Type "ps aux | llm_grep "
Sleep 300ms
Type@30ms `"top 3 processes by memory usage"`
Sleep 1s
Enter
Sleep 5s
Sleep 2s

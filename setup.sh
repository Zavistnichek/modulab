#!/bin/bash

# Variable for the repository path
REPO_DIR="${1:-$HOME/daily-python-journey}"

# Creating the directory structure
mkdir -p "$REPO_DIR" && cd "$REPO_DIR" || exit

# Function to create files for each day
create_day_files() {
    local day="$1"
    case $day in
        01) touch "day_$day"/{bmi_calculator.py,temperature_converter.py} ;;
        02) touch "day_$day"/{password_generator.py,reverse_string.py} ;;
        03) touch "day_$day"/{guess_the_number.py,prime_numbers.py} ;;
        04) touch "day_$day"/{basic_list_operations.py,string_formatter.py} ;;
        05) touch "day_$day"/{tic_tac_toe.py,rock_paper_scissors.py} ;;
        06) touch "day_$day"/{todo_list.py,habit_tracker.py} ;;
        07) touch "day_$day"/{magic_8_ball.py,word_counter.py} ;;
        08) touch "day_$day"/{palindrome_checker.py,function_calculator.py} ;;
        09) touch "day_$day"/{phone_book.py,friends_manager.py} ;;
        10) touch "day_$day"/{mood_diary.py,export_to_json.py} ;;
        11) touch "day_$day"/{safe_calculator.py,email_validator.py} ;;
        12) touch "day_$day"/{random_date_generator.py,time_converter.py} ;;
        13) touch "day_$day"/{password_validator.py,regex_email_checker.py} ;;
        14) touch "day_$day"/{log_parser.py,chat_filter.py} ;;
        15) touch "day_$day"/{rpg_game.py,inventory_system.py} ;;
        16) touch "day_$day"/{csv_tool.py,sales_analyzer.py} ;;
        17) touch "day_$day"/{telegram_bot.py,simple_web_scraper.py} ;;
        18) touch "day_$day"/{weather_api_fetcher.py,news_aggregator.py} ;;
        19) touch "day_$day"/{task_scheduler.py,habit_reminder.py} ;;
        20) touch "day_$day"/{stock_price_tracker.py,crypto_price_alert.py} ;;
        21) touch "day_$day"/{file_organizer.py,duplicate_finder.py} ;;
        22) touch "day_$day"/{data_visualization.py,simple_dashboard.py} ;;
        23) touch "day_$day"/{basic_flask_app.py,url_shortener.py} ;;
        24) touch "day_$day"/{django_blog.py,user_auth_system.py} ;;
        25) touch "day_$day"/{notebook_app.py,calendar_reminder.py} ;;
        26) touch "day_$day"/{voice_assistant.py,speech_to_text.py} ;;
        27) touch "day_$day"/{face_recognition.py,qr_code_generator.py} ;;
        28) touch "day_$day"/{simple_ai_chatbot.py,language_translator.py} ;;
        29) touch "day_$day"/{code_analyzer.py,unit_test_generator.py} ;;
        30) touch "day_$day"/{certificate_generator.py,final_project.py} ;;
    esac
}

# Automating the file creation for each day
for day in {01..30}; do
    mkdir -p "day_$day"
    create_day_files "$day"
done

# Generate README in English
cat <<EOL > README.md
# 🚀 30-Day Python Journey

This repository contains a **30-day Python challenge**.  
Each day includes **2-3 mini-projects** to reinforce skills.

## 🔥 How to use:  
1. Clone the repository:  
   \`\`\`bash  
   git clone https://github.com/your_username/daily-python-journey.git  
   cd daily-python-journey  
   \`\`\`  
2. Choose a day, go to the corresponding folder, and start coding!

## 📌 Progress:
| Day       | Status | Tasks Completed |
|-----------|--------|-----------------|
| 01        | ✅     | 2/2             |
| 02        | 🚧     | 1/2             |
| ...       | ...    | ...             |

🎯 **Goal**:  
By the end of 30 days, you'll have:
✔ 50+ working projects for your portfolio  
✔ Confident Python skills for real-world tasks  
✔ Experience with documentation and debugging  

**Important:** All projects are written without autocompletion!

EOL

# Initialize Git repository
git init
git add .
git commit -m "Init: 30-day Python challenge structure"

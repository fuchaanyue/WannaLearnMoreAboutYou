import os
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMessage, get_connection
from qcloud_cos.cos_client import CosConfig
from qcloud_cos.cos_client import CosS3Client
import sys
import logging
from decouple import config
import threading
import time
import socket

def get_quiz_questions():
    """
    获取测验题目和提示（硬编码在代码中）
    答案从环境变量中获取，如果环境变量中没有提供答案，则使用占位符
    """
    try:
        answers_json = config('QUIZ_ANSWERS', default=None)
        if answers_json:
            answers = json.loads(answers_json)
        else:
            answers = []
    except:
        answers = []
    
    # 使用环境变量中的答案，如果未提供则使用占位符
    answer1 = answers[0]
    answer2 = answers[1]
    answer3 = answers[2]
    
    return [
        {
            "text": "付安粤同学在首都师范大学第四十届校园歌手大赛——SOSTAR SINGER“闪耀的我们”2025星辰歌会中的个人演唱曲目是？",
            "answer": answer1,
            "hints": [
                {"type": "image", "content": "/static/hint1.jpg"},  # 第一个提示是图片
                {"type": "text", "content": "psdph"},  # 第二个提示是文字
                {"type": "text", "content": "活力调频视频号直播回放"},  # 第三个提示是文字
                {"type": "image", "content": "/static/hint4.png"},  # 第四个提示是图片
                {"type": "text", "content": "直播回放时间戳95‘20”"}  # 第五个提示是文字
            ]
        },
        {
            "text": "看看能不能从模糊的高中毕业照中找出我嘿嘿（四位阿拉伯数字坐标，从下往上从左往右，如第九排第六十个0960）",
            "answer": answer2,
            "image": "/static/graduation_photo.jpg",  # 毕业照图片路径
            "hints": [  # 添加提示
                {"type": "text", "content": "短发男孩"},  # 第一个提示是文字
                {"type": "text", "content": "没什么可提示的了哈哈哈"}  # 第二个提示是文字
            ]
        },
        {
            "text": "dddz制作的一个小短片《叫魂WAKEUP》里有一段关于我与时间的关系思考，其中的第56个字是？",
            "answer": answer3,
            "hints": [
                {"type": "text", "content": "在视频号ssjsjhhjbb可以找到该视频"},
                {"type": "text", "content": "02‘00“开始"}
            ]
        }
    ]

def get_quiz_answers():
    """
    从环境变量中获取测验答案
    如果环境变量中没有配置，则使用默认答案
    """
    try:
        answers_json = config('QUIZ_ANSWERS', default=None)
        if answers_json:
            return json.loads(answers_json)
    except:
        pass
    
    # 默认答案（仅在环境变量未配置时使用）
    return ["", "", ""]

def index(request):
    if request.method == "POST":
        user_name = request.POST.get("name", "")
        # Save the user's name in session
        if user_name:
            request.session["user_name"] = user_name
            # Redirect to second page instead of feedback
            return redirect("second_page")
        else:
            return render(request, "quiz/index.html", {
                "error": "请输入您的姓名。",
            })
    
    return render(request, "quiz/index.html")

def second_page(request):
    # Check if user has provided their name
    if "user_name" not in request.session:
        return redirect("index")
        
    # Get user name from session
    user_name = request.session.get("user_name", "朋友")
    return render(request, "quiz/second_page.html", {
        "user_name": user_name
    })

def quiz(request):
    # Check if user has provided their name
    if "user_name" not in request.session:
        return redirect("index")
    
    # Get user name from session
    user_name = request.session.get("user_name", "朋友")
    
    # Get questions (with answers from environment variables)
    questions = get_quiz_questions()
    
    # Get current question index
    question_index = request.session.get("quiz_progress", 0)
    
    # Ensure question_index is within bounds
    if question_index >= len(questions):
        question_index = 0
        request.session["quiz_progress"] = 0
        request.session.modified = True
    
    # Check if this is a question with hints
    total_hints = len(questions[question_index]["hints"]) if "hints" in questions[question_index] else 0
    
    # Reset hint index for current question
    request.session["hint_index"] = 0
    request.session.modified = True
    
    # Display current question with no hints initially
    return render(request, "quiz/quiz.html", {
        "user_name": user_name,
        "question": questions[question_index],
        "question_number": question_index + 1,
        "total_questions": len(questions),
        "hint_index": 0,
        "total_hints": total_hints
    })

def previous_question(request):
    # Check if user has provided their name
    if "user_name" not in request.session:
        return redirect("index")
    
    # Get questions (with answers from environment variables)
    questions = get_quiz_questions()
    
    # Get current question index
    question_index = request.session.get("quiz_progress", 0)
    
    # Move to previous question if not on the first question
    if question_index > 0:
        question_index -= 1
        request.session["quiz_progress"] = question_index
        request.session.modified = True
    
    # Redirect to quiz view to show the previous question
    return redirect("quiz")

def quiz_with_hint(request, hint_index):
    # Check if user has provided their name
    if "user_name" not in request.session:
        return redirect("index")
    
    # Get user name from session
    user_name = request.session.get("user_name", "朋友")
    
    # Get questions (with answers from environment variables)
    questions = get_quiz_questions()
    
    # Get current question index
    question_index = request.session.get("quiz_progress", 0)
    
    # Ensure question_index is within bounds
    if question_index >= len(questions):
        question_index = 0
        request.session["quiz_progress"] = 0
        request.session.modified = True
    
    # Check if this is a question with hints
    total_hints = len(questions[question_index]["hints"]) if "hints" in questions[question_index] else 0
    
    # Update session hint index
    request.session["hint_index"] = hint_index
    request.session.modified = True
    
    # Prepare all hints up to the current index in reverse order (newest first)
    displayed_hints = []
    for i in range(hint_index - 1, -1, -1):  # Reverse iteration
        if "hints" in questions[question_index] and i < len(questions[question_index]["hints"]):
            displayed_hints.append({
                "hint": questions[question_index]["hints"][i],
                "index": i + 1
            })
    
    return render(request, "quiz/quiz.html", {
        "user_name": user_name,
        "question": questions[question_index],
        "question_number": question_index + 1,
        "total_questions": len(questions),
        "displayed_hints": displayed_hints,
        "hint_index": hint_index,
        "total_hints": total_hints
    })

def quiz_with_hint_error(request, hint_index, error):
    # Check if user has provided their name
    if "user_name" not in request.session:
        return redirect("index")
    
    # Get user name from session
    user_name = request.session.get("user_name", "朋友")
    
    # Get questions (with answers from environment variables)
    questions = get_quiz_questions()
    
    # Get current question index
    question_index = request.session.get("quiz_progress", 0)
    
    # Ensure question_index is within bounds
    if question_index >= len(questions):
        question_index = 0
        request.session["quiz_progress"] = 0
        request.session.modified = True
    
    # Check if this is a question with hints
    total_hints = len(questions[question_index]["hints"]) if "hints" in questions[question_index] else 0
    
    # Update session hint index
    request.session["hint_index"] = hint_index
    request.session.modified = True
    
    # Prepare all hints up to the current index in reverse order (newest first)
    displayed_hints = []
    for i in range(hint_index - 1, -1, -1):  # Reverse iteration
        if "hints" in questions[question_index] and i < len(questions[question_index]["hints"]):
            displayed_hints.append({
                "hint": questions[question_index]["hints"][i],
                "index": i + 1
            })
    
    return render(request, "quiz/quiz.html", {
        "user_name": user_name,
        "question": questions[question_index],
        "question_number": question_index + 1,
        "total_questions": len(questions),
        "displayed_hints": displayed_hints,
        "hint_index": hint_index,
        "total_hints": total_hints,
        "error": error
    })

def handle_quiz_post(request):
    # Check if user has provided their name
    if "user_name" not in request.session:
        return redirect("index")
    
    # Get user name from session
    user_name = request.session.get("user_name", "朋友")
    
    # Get questions (with answers from environment variables)
    questions = get_quiz_questions()
    
    # Get current question index
    question_index = request.session.get("quiz_progress", 0)
    
    # Ensure question_index is within bounds
    if question_index >= len(questions):
        question_index = 0
        request.session["quiz_progress"] = 0
        request.session.modified = True
    
    # Process form submission
    if "hint" in request.POST:
        hint_index = request.session.get("hint_index", 0)
        # Only process hint if there are more hints available
        if "hints" in questions[question_index] and hint_index < len(questions[question_index]["hints"]):
            request.session["hint_index"] = hint_index + 1
            request.session.modified = True
            # Redirect to avoid POST refresh warning
            return redirect("quiz_with_hint", hint_index=hint_index + 1)
        elif "hints" not in questions[question_index]:
            # For questions without hints, just redirect back without changes
            return redirect("quiz")
        else:
            # If no more hints, redirect to current state without changes
            return redirect("quiz_with_hint", hint_index=hint_index)
    
    # Handle answer submission
    user_answer = request.POST.get("answer", "").strip()
    # Check if user provided an answer
    if not user_answer:
        # Redirect with error for empty answer
        hint_index = request.session.get("hint_index", 0)
        return redirect("quiz_with_hint_error", hint_index=hint_index, error="请输入答案。")
    
    correct_answer = questions[question_index]["answer"]
    
    if user_answer.lower() == correct_answer.lower():
        # Move to next question or finish quiz
        request.session["quiz_progress"] = question_index + 1
        request.session.modified = True
        
        # Check if quiz is completed
        if request.session["quiz_progress"] >= len(questions):
            # Mark quiz as passed
            request.session["quiz_passed"] = True
            request.session.modified = True
            # Redirect to thank you page instead of feedback
            return redirect("thank_you")
        else:
            # Reset hint index for next question
            request.session["hint_index"] = 0
            request.session.modified = True
            # Redirect to next question
            return redirect("quiz")
    else:
        # Redirect with error for wrong answer
        hint_index = request.session.get("hint_index", 0)
        return redirect("quiz_with_hint_error", hint_index=hint_index, error="答案不正确，请再试一次。")

def feedback(request):
    # 记录请求信息用于调试
    print(f"Feedback view called with method: {request.method}")
    
    # Check if user has passed the quiz
    if not request.session.get("quiz_passed", False):
        print("User has not passed the quiz, redirecting to index")
        return redirect("index")
    
    # Get user name from session
    user_name = request.session.get("user_name", "朋友")
    print(f"User name: {user_name}")
    
    if request.method == "POST":
        try:
            print("Processing POST request")
            # 获取所有问题的答案
            question1 = request.POST.get("question1", "").strip()
            question2 = request.POST.get("question2", "").strip()
            question3 = request.POST.get("question3", "").strip()
            feedback_text = request.POST.get("feedback", "").strip()
            
            print(f"Form data - Q1: {question1}, Q2: {question2}, Q3: {question3}, Feedback: {feedback_text}")
            
            # 检查必填项
            if not question1 or not question2:
                # 如果必填项为空，返回错误信息
                print("Required fields are missing")
                return render(request, "quiz/feedback.html", {
                    "user_name": user_name,
                    "error": "请填写所有必填项（带 * 的问题）。",
                    "question1": question1,
                    "question2": question2,
                    "question3": question3,
                    "feedback_text": feedback_text
                })
            
            # 整合用户提交的所有数据
            # 获取北京时间
            beijing_time = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))
            user_data = {
                "user_name": user_name,
                "question1": {
                    "question": "1. 如果可以选择变成任意的东西，你想变成些什么，能说说你的想法吗？",
                    "answer": question1
                },
                "question2": {
                    "question": "2. 很好奇我留给你的初印象是什么？",
                    "answer": question2
                },
                "question3": {
                    "question": "3. 有没有什么东西是我不知道但你能告诉我的？（不强求哈哈哈哈哈）",
                    "answer": question3
                },
                "feedback": {
                    "question": "4. 还有其他想对我说的吗？",
                    "answer": feedback_text
                },
                "timestamp": beijing_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 保存到会话中以便在thank_you页面使用
            request.session['feedback_data'] = user_data
            request.session.modified = True
            
            # 将数据转换为纯文本格式用于发送邮件和保存
            text_data = f"""用户反馈数据
================

用户名: {user_data['user_name']}
提交时间: {user_data['timestamp']}

问题1: {user_data['question1']['question']}
回答1: {user_data['question1']['answer']}

问题2: {user_data['question2']['question']}
回答2: {user_data['question2']['answer']}

问题3: {user_data['question3']['question']}
回答3: {user_data['question3']['answer']}

问题4: {user_data['feedback']['question']}
回答4: {user_data['feedback']['answer']}"""
            
            # 发送邮件
            try:
                print(f"尝试发送邮件: EMAIL_HOST={settings.EMAIL_HOST}, EMAIL_PORT={settings.EMAIL_PORT}, EMAIL_HOST_USER={settings.EMAIL_HOST_USER}")
                if settings.EMAIL_HOST_USER:
                    # 生成文件名（使用用户名和时间戳）
                    timestamp = beijing_time.strftime("%Y%m%d_%H%M%S")
                    filename = f"{user_name}_{timestamp}.txt"
                    
                    # 创建邮件
                    email = EmailMessage(
                        subject=f'用户反馈 - {user_name}',
                        body='这是一份来自网站的用户反馈，请查看附件中的文本文件。',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[settings.EMAIL_HOST_USER],  # 发送给自己
                    )
                    email.attach(filename, text_data, 'text/plain')
                    
                    # 使用线程发送邮件以避免阻塞
                    def send_email_async(email):
                        try:
                            print(f"开始发送邮件到: {settings.EMAIL_HOST_USER}")
                            # 显式创建连接以获得更好的错误处理
                            connection = get_connection(
                                backend=settings.EMAIL_BACKEND,
                                host=settings.EMAIL_HOST,
                                port=settings.EMAIL_PORT,
                                username=settings.EMAIL_HOST_USER,
                                password=settings.EMAIL_HOST_PASSWORD,
                                use_tls=settings.EMAIL_USE_TLS,
                            )
                            
                            # 尝试连接到SMTP服务器
                            print(f"正在连接到SMTP服务器: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
                            connection.open()
                            print("SMTP连接成功")
                            
                            # 发送邮件
                            result = email.send()
                            print(f"邮件发送结果: {result}")
                            if result == 0:
                                print("警告：邮件发送可能失败，返回值为0")
                            else:
                                print(f"邮件发送成功，发送了 {result} 封邮件")
                            
                            # 关闭连接
                            connection.close()
                        except socket.gaierror as e:
                            print(f"DNS解析错误，无法解析SMTP主机: {e}")
                            print("请检查EMAIL_HOST配置是否正确")
                        except socket.timeout as e:
                            print(f"连接SMTP服务器超时: {e}")
                            print("可能是网络问题或SMTP服务器不可达")
                        except ConnectionRefusedError as e:
                            print(f"连接被SMTP服务器拒绝: {e}")
                            print("请检查EMAIL_PORT配置或SMTP服务器状态")
                        except OSError as e:
                            if e.errno == 101:  # Network is unreachable
                                print("网络不可达错误: 无法连接到SMTP服务器")
                                print("这可能是因为部署环境的网络限制导致的")
                                print("建议检查防火墙设置或联系平台支持")
                            else:
                                print(f"网络连接错误: {e}")
                        except Exception as e:
                            import traceback
                            print(f"异步发送邮件失败: {e}")
                            print(f"详细错误信息: {traceback.format_exc()}")
                            # 尝试关闭连接（如果打开的话）
                            try:
                                connection.close()
                            except:
                                pass
                    
                    email_thread = threading.Thread(target=send_email_async, args=(email,))
                    email_thread.daemon = True  # 设置为守护线程
                    email_thread.start()
                    
                    print("邮件发送任务已启动（异步）")
                else:
                    print("未配置邮箱用户，跳过发送邮件")
            except Exception as e:
                # 记录邮件发送错误但不中断流程
                import traceback
                print(f"发送邮件失败: {e}")
                print(f"详细错误信息: {traceback.format_exc()}")
            
            # 保存到腾讯云COS
            try:
                # 创建COS客户端
                if settings.TENCENT_COS_SECRET_ID and settings.TENCENT_COS_SECRET_KEY:
                    config = CosConfig(
                        Region=settings.TENCENT_COS_REGION,
                        SecretId=settings.TENCENT_COS_SECRET_ID,
                        SecretKey=settings.TENCENT_COS_SECRET_KEY
                    )
                    client = CosS3Client(config)
                    
                    # 生成文件名（使用用户名和时间戳）
                    timestamp = beijing_time.strftime("%Y%m%d_%H%M%S")
                    filename = f"feedback/{user_name}_{timestamp}.txt"
                    
                    # 使用线程上传到COS以避免阻塞
                    def upload_to_cos_async(client, bucket, body, key):
                        try:
                            # 添加更多调试信息
                            print(f"尝试上传到COS: bucket={bucket}, region={settings.TENCENT_COS_REGION}")
                            response = client.put_object(
                                Bucket=bucket,
                                Body=body,
                                Key=key,
                                EnableMD5=False
                            )
                            print(f"COS上传成功: {response}")
                        except Exception as e:
                            import traceback
                            print(f"异步上传到COS失败: {e}")
                            print(f"详细错误信息: {traceback.format_exc()}")
                    
                    cos_thread = threading.Thread(target=upload_to_cos_async, args=(client, settings.TENCENT_COS_BUCKET, text_data, filename))
                    cos_thread.daemon = True  # 设置为守护线程
                    cos_thread.start()
                    
                    print("COS上传任务已启动（异步）")
            except Exception as e:
                # 如果COS上传失败，记录详细错误但不中断流程
                import traceback
                print(f"上传到COS失败: {e}")
                print(f"详细错误信息: {traceback.format_exc()}")
                print(f"检查配置 - SECRET_ID: {bool(settings.TENCENT_COS_SECRET_ID)}")
                print(f"检查配置 - SECRET_KEY: {bool(settings.TENCENT_COS_SECRET_KEY)}")
                print(f"检查配置 - REGION: {settings.TENCENT_COS_REGION}")
                print(f"检查配置 - BUCKET: {settings.TENCENT_COS_BUCKET}")
            
            # 重定向到thank_you_after_feedback页面
            print("Redirecting to thank_you_after_feedback")
            return redirect('thank_you_after_feedback')
        except Exception as e:
            # 捕获所有其他异常并记录错误
            import traceback
            print(f"反馈处理过程中发生错误: {e}")
            print(f"详细错误信息: {traceback.format_exc()}")
            # 即使出现错误也重定向到感谢页面，避免用户看到500错误
            return redirect('thank_you_after_feedback')
        
    # GET请求时显示表单
    print("Rendering feedback form")
    return render(request, "quiz/feedback.html", {
        "user_name": user_name
    })

def thank_you(request):
    # Check if user has passed the quiz
    if not request.session.get("quiz_passed", False):
        return redirect("index")
    
    # Get user name from session
    user_name = request.session.get("user_name", "朋友")
    
    # 获取反馈数据（如果存在）
    feedback_data = request.session.get('feedback_data', None)
    
    return render(request, "quiz/thank_you.html", {
        "user_name": user_name,
        "feedback_data": feedback_data
    })

def thank_you_after_feedback(request):
    # Check if user has passed the quiz
    if not request.session.get("quiz_passed", False):
        return redirect("index")
    
    # Get user name from session
    user_name = request.session.get("user_name", "朋友")
    
    return render(request, "quiz/thank_you_after_feedback.html", {
        "user_name": user_name
    })

def qrcode_image(request):
    # Check if user has passed the quiz
    if not request.session.get("quiz_passed"):
        return HttpResponseForbidden("Access denied")
    
    try:
        # Check if we're in Render environment
        import os
        if 'RENDER' in os.environ:
            # In Render, use the mounted file with correct extension
            qr_code_path = Path('/etc/secrets/wechat_qr.jpg')
            print(f"在Render环境中查找二维码: {qr_code_path}")
        else:
            # Local development or other environments
            from django.conf import settings
            qr_code_path = settings.PRIVATE_FILES_DIR / "wechat_qr.jpg"
            print(f"在本地环境中查找二维码: {qr_code_path}")
        
        print(f"二维码路径是否存在: {qr_code_path.exists()}")
        if not qr_code_path.exists():
            print(f"二维码文件未找到: {qr_code_path}")
            return HttpResponse("QR code image not found", status=404)
        
        print(f"成功找到二维码文件: {qr_code_path}")
        # 使用FileResponse返回图片
        return FileResponse(open(qr_code_path, 'rb'), content_type='image/jpeg')
    except Exception as e:
        # Handle any exceptions that might occur
        import traceback
        print(f"二维码加载错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return HttpResponse("QR code image not found", status=404)

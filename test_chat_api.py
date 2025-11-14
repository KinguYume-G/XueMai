"""
测试聊天API端点
运行: python test_chat_api.py
"""

import requests
import json

# 配置
BASE_URL = "http://127.0.0.1:8000/api"

def test_api():
    print("=" * 60)
    print("聊天系统 API 测试")
    print("=" * 60)

    # 1. 获取一个测试用户的token
    print("\n[1] 登录测试用户...")

    # 首先获取所有用户列表（需要先登录一个admin用户或使用Django shell）
    # 这里我们假设已经有一个用户Jeffrey的token

    # 测试用例：不带认证直接访问API（应该返回401）
    print("\n[2] 测试未认证访问...")
    response = requests.get(f"{BASE_URL}/social/chat/friends/")
    print(f"  状态码: {response.status_code}")
    if response.status_code == 401:
        print("  ✅ 正确返回401 - 需要认证")
    else:
        print(f"  ❌ 异常 - 响应: {response.text}")

    # 获取测试token
    print("\n[3] 尝试登录获取token...")
    # 你需要提供一个真实的测试用户名和密码
    login_data = {
        "username": "Jeffrey",  # 替换为实际用户名
        "password": "password123"  # 替换为实际密码
    }

    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )

        if login_response.status_code == 200:
            token_data = login_response.json()
            if 'data' in token_data and 'access' in token_data['data']:
                access_token = token_data['data']['access']
                print(f"  ✅ 登录成功")

                # 使用token测试各个API端点
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                # 测试好友列表API
                print("\n[4] 测试好友列表 API...")
                friends_response = requests.get(
                    f"{BASE_URL}/social/chat/friends/",
                    headers=headers
                )
                print(f"  状态码: {friends_response.status_code}")
                if friends_response.status_code == 200:
                    friends_data = friends_response.json()
                    print(f"  ✅ 成功获取好友列表")
                    print(f"  好友数量: {friends_data.get('count', 0)}")
                    if friends_data.get('results'):
                        print(f"  前3个好友:")
                        for friend in friends_data['results'][:3]:
                            username = friend.get('user', {}).get('username', 'Unknown')
                            unread = friend.get('unread_count', 0)
                            print(f"    - {username} (未读: {unread})")
                else:
                    print(f"  ❌ 失败: {friends_response.text}")

                # 测试关注列表API
                print("\n[5] 测试关注列表 API...")
                following_response = requests.get(
                    f"{BASE_URL}/social/chat/following/",
                    headers=headers
                )
                print(f"  状态码: {following_response.status_code}")
                if following_response.status_code == 200:
                    following_data = following_response.json()
                    print(f"  ✅ 成功获取关注列表")
                    print(f"  关注数量: {following_data.get('count', 0)}")
                else:
                    print(f"  ❌ 失败: {following_response.text}")

                # 测试粉丝列表API
                print("\n[6] 测试粉丝列表 API...")
                followers_response = requests.get(
                    f"{BASE_URL}/social/chat/followers/",
                    headers=headers
                )
                print(f"  状态码: {followers_response.status_code}")
                if followers_response.status_code == 200:
                    followers_data = followers_response.json()
                    print(f"  ✅ 成功获取粉丝列表")
                    print(f"  粉丝数量: {followers_data.get('count', 0)}")
                else:
                    print(f"  ❌ 失败: {followers_response.text}")

                # 测试群组列表API
                print("\n[7] 测试群组列表 API...")
                groups_response = requests.get(
                    f"{BASE_URL}/social/chat/groups/",
                    headers=headers
                )
                print(f"  状态码: {groups_response.status_code}")
                if groups_response.status_code == 200:
                    groups_data = groups_response.json()
                    print(f"  ✅ 成功获取群组列表")
                    print(f"  群组数量: {groups_data.get('count', 0)}")
                else:
                    print(f"  ❌ 失败: {groups_response.text}")

                # 测试好友申请列表API
                print("\n[8] 测试好友申请列表 API...")
                requests_response = requests.get(
                    f"{BASE_URL}/social/chat/friend-requests/",
                    headers=headers
                )
                print(f"  状态码: {requests_response.status_code}")
                if requests_response.status_code == 200:
                    requests_data = requests_response.json()
                    print(f"  ✅ 成功获取好友申请列表")
                    print(f"  待处理申请数量: {requests_data.get('count', 0)}")
                else:
                    print(f"  ❌ 失败: {requests_response.text}")

                # 测试未读消息数API
                print("\n[9] 测试未读消息数 API...")
                unread_response = requests.get(
                    f"{BASE_URL}/social/chat/unread-count/",
                    headers=headers
                )
                print(f"  状态码: {unread_response.status_code}")
                if unread_response.status_code == 200:
                    unread_data = unread_response.json()
                    print(f"  ✅ 成功获取未读消息数")
                    print(f"  未读消息总数: {unread_data.get('total_unread', 0)}")
                else:
                    print(f"  ❌ 失败: {unread_response.text}")

            else:
                print(f"  ❌ 登录响应格式错误: {token_data}")
        else:
            print(f"  ❌ 登录失败 (状态码: {login_response.status_code})")
            print(f"  响应: {login_response.text}")
            print("\n  提示: 请确保:")
            print("  1. 用户名和密码正确")
            print("  2. 后端服务器正在运行")
            print("  3. 数据库中存在该用户")

    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        print("\n  提示: 请确保后端服务器正在运行在 http://127.0.0.1:8000")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_api()

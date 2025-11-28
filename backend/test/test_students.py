def test_create_student(client):
    # 1. 准备测试数据
    student_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@warwick.ac.uk"
    }

    # 2. 发送 POST 请求 (这个端点目前还不存在)
    response = client.post("/students/", json=student_data)

    # 3. 断言 (Expectations)
    # 我们期望返回 200 或 201 状态码
    assert response.status_code == 200 
    data = response.json()
    
    # 验证返回的数据是否包含我们发送的内容，并且有了数据库生成的 ID
    assert data["email"] == "alice.smith@warwick.ac.uk"
    assert "id" in data
    assert isinstance(data["id"], int)
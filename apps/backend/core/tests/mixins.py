class UUIDAssertionsMixin:
    def assert_uuid_equal(self, left, right):
        self.assertEqual(str(left), str(right))


class StandardResponseAssertionsMixin:
    def assert_success_response(self, response, *, status_code, code=None, message=None):
        self.assertEqual(response.status_code, status_code)
        self.assertTrue(response.data["success"])

        if code is not None:
            self.assertEqual(response.data["code"], code)
        if message is not None:
            self.assertEqual(response.data["message"], message)

    def assert_error_response(self, response, *, status_code, code=None, message=None):
        self.assertEqual(response.status_code, status_code)
        self.assertFalse(response.data["success"])

        if code is not None:
            self.assertEqual(response.data["code"], code)
        if message is not None:
            self.assertEqual(response.data["message"], message)


class APIClientMixin:
    def authenticate(self, user):
        self.client.force_authenticate(user)

    def get_json(self, path, data=None, **kwargs):
        return self.client.get(path, data=data, format="json", **kwargs)

    def post_json(self, path, data=None, **kwargs):
        return self.client.post(path, data=data, format="json", **kwargs)

    def patch_json(self, path, data=None, **kwargs):
        return self.client.patch(path, data=data, format="json", **kwargs)

    def put_json(self, path, data=None, **kwargs):
        return self.client.put(path, data=data, format="json", **kwargs)

    def delete_json(self, path, data=None, **kwargs):
        return self.client.delete(path, data=data, format="json", **kwargs)

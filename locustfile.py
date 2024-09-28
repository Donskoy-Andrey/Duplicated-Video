import random
from locust import HttpUser, task, between

urls = [
    'https://s3.ritm.media/yappy-db-duplicates/5eb4127e-5694-492b-963c-6688522e9ad2.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/b5f191e6-42e0-43f5-8773-560643de17fb.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/025ee26a-7391-4f60-878a-7fc1928a967b.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/a18324cf-b2ad-41e2-86b8-e6923c5fdc36.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/2253aaa4-b29c-4b7d-b9cc-9286d23c44e8.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/99c8cd59-5995-4981-8346-460d40e4eed3.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/5acd8e68-99fe-43fd-b9f9-b2279bdc9372.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/05d72fc9-89a3-47bf-bb1b-6db4fc6f2b56.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/36e972c3-7134-41ce-b37f-e227fece4575.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/21caaf15-da57-431d-80bf-add3554a5471.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/d5a555f7-9fe9-49e6-b0d5-de096ea7160a.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/27b07648-d7e8-42e3-9131-5a43e3e4f31f.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/390f73b5-6e10-4db6-978d-03cf06d2cc39.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/a43f84bf-6822-478d-b20d-aacbbb76c436.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/35e62643-9df2-4db8-9e3a-046c5d44e45e.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/0809df66-746d-48ae-a412-801b1d14ef71.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/21a93966-f283-4389-a818-a7154d072d07.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/54c01dff-ad81-46d5-b4d6-0a433760ae62.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/b8b53fd0-5f5e-4054-bf36-a4d6127d1cd4.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/63b899be-9547-44c2-91b2-e1b71510a614.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/1ad0536e-8422-409f-9e4a-3dc64f5e260a.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/b5699703-e75a-4ea4-a8f0-1327108be3cb.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/5294cc15-7f66-4361-af49-18369ae2717c.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/b7defd6d-f2ba-4dec-b341-0a04f471a721.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/e5b901b2-5363-4ee3-9fb9-c8562734d0bc.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/d7009e84-c4fd-4591-abcb-124332e1746d.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/f7b9fc3c-f6fc-4102-90c7-33361763333f.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/a8ed78f8-905d-420d-9a66-ade97947c465.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/beb24e8f-be76-4588-a51b-060e82dc3df0.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/fd039f07-4626-460d-9ec4-a30748cc19a3.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/ddb2778d-7c4e-4f50-9c5a-880b7d77b08b.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/90cef144-86de-4026-87ac-f4b04254d865.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/da83a216-cea6-4a81-9db9-566d6c5d2c54.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/fab21d73-6119-436d-bb17-97b25e8858ff.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/4904f2e0-0876-4f25-bba3-97806456bd31.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/46f9cac3-f0d5-4e8b-9937-259b92321421.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/c8efc573-2587-447f-8290-917b05ddb2ca.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/48a94012-0cba-48af-a7c9-7b46efdf609e.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/8ac4cfcb-ef27-4634-b287-7afaa55b1834.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/70087c05-e42f-4dbc-943f-dea1e168cd75.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/7da7d097-b2e8-4b2f-b8ce-b3bb62752d54.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/4e13f784-dc74-4532-b944-1789b3a95af1.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/ad06c636-19a4-4da8-b3c7-d5fe2e55f444.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/6c6ac260-0d07-4192-ac3c-eaaa39a83cd5.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/a53dc1ea-66e3-4e15-bcf3-c4e67a9b37ab.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/e05cb4c8-08c3-4cdc-9dc6-75b80555a4d4.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/3831c5e4-e96e-4f4a-8cac-a03e233142a9.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/98b857f9-7a04-499c-b929-385a944d757c.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/86b62ece-aa13-4b92-8085-3fb8e5aaadae.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/c318bca6-515c-4c33-961c-4c42a42d448d.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/5ed0d616-934c-4101-b665-bf16d9f1c443.mp4',
     'https://s3.ritm.media/yappy-db-duplicates/4afe4f5b-61f8-4e2c-8712-28eb8eac610e.mp4'
 ]


class VideoDuplicateTestUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def check_video_duplicate(self):
        url = "/check-video-duplicate"
        body = {
            "link": random.choice(urls)
        }
        response = self.client.post(url, json=body)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")




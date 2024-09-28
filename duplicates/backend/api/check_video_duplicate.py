# from typing import Tuple
#
# import faiss
# import requests
# from fastapi import HTTPException
# from torch.nn.functional import embedding
# import tritonclient.http as httpclient
#
# from duplicates.backend.api.convert_url_to_tenzor import video_url_to_tensor
# from duplicates.backend.api.video_link_request import VideoLinkRequest
# from duplicates.backend.api.video_link_response import VideoLinkResponse
#
# import torch
# import tritonclient.http as httpclient
# import numpy as np
#
#
# def search_nearest_vector(embeddings) -> Tuple[bool, str|None]:
#     return True, '23fac2f2-7f00-48cb-b3ac-aac8caa3b6b4'
#
#
# def send_video_to_triton(video_tensor, server_url="localhost:5000"):
#     embeddings = [1,3,5,7,68,4664454,6564,78,2,5,5,9,3,41,8,5,27,3,1,8,6,1,8,9]
#     return embeddings
#     triton_client = httpclient.InferenceServerClient(url=server_url)
#     video_np = video_tensor.cpu().numpy().astype(np.float32)
#     inputs = []
#     input_tensor = httpclient.InferInput('INPUT__0', video_np.shape, "FP32")
#     input_tensor.set_data_from_numpy(video_np)
#     inputs.append(input_tensor)
#
#     outputs = []
#     outputs.append(httpclient.InferRequestedOutput('OUTPUT__0'))
#
#     response = triton_client.infer(
#         model_name='video-embedder',
#         inputs=inputs,
#         outputs=outputs
#     )
#
#     embeddings = response.as_numpy('OUTPUT__0')
#     embeddings = [1,3,5,7,68,4664454,6564,78,2,5,5,9,3,41,8,5,27,3,1,8,6,1,8,9]
#     return embeddings
#
#
# def check_video_duplicate(link_request: VideoLinkRequest):
#     """
#
#     :param link_request:
#     :return:
#     """
#     """ тут еще логика проверки url"""
#     video_tensor = video_url_to_tensor(str(link_request.link))
#     embedding = send_video_to_triton(video_tensor)
#     print(f"{embedding=}")
#
#     is_duplicate, duplicate_video_id = search_nearest_vector(embedding)
#
#     if is_duplicate:
#         return VideoLinkResponse(
#             is_duplicate=True,
#             duplicate_for=duplicate_video_id
#         )
#     else:
#         return VideoLinkResponse(
#             is_duplicate=False,
#             duplicate_for=None
#         )


from dataclasses import dataclass
from typing import Optional, Tuple, List

import asyncio
import cv2
import numpy as np
import torch
import tritonclient.http as httpclient
from fastapi import FastAPI, HTTPException
import tritonclient.grpc as grpcclient

from .convert_url_to_tenzor import VideoTransform
from .video_link_request import VideoLinkRequest
from .video_link_response import VideoLinkResponse


class VideoDuplicateChecker:
    def __init__(
            self,
            server_url_triton: str = "triton:8004",
            model_name: str = "video-embedder",

    ):
        self.server_url_triton = server_url_triton
        self.model_name = model_name
        self.triton_client = grpcclient.InferenceServerClient(url=self.server_url_triton)

    async def video_url_to_tensor(self, url: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Асинхронно загружает видео по URL и преобразует его в тензоры.
        """
        print("Асинхронно загружает видео по URL и преобразует его в тензоры.")
        return await asyncio.to_thread(self._video_url_to_tensor, url)

    def _video_url_to_tensor(self, url: str) -> Tuple[torch.Tensor, torch.Tensor]:
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            raise ValueError(f"Не удалось открыть видео по URL: {url}")
        print('Файл открыт ')
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames = []
        for i in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_tensor = torch.from_numpy(frame_rgb).permute(2, 0, 1)  # (H, W, C) -> (C, H, W)
            frames.append(frame_tensor)
        cap.release()
        frames = torch.stack(frames)
        frames = frames.permute(1, 0, 2, 3)
        transform = VideoTransform()
        video_tensor_short, video_tensor_long = transform({"video": frames})["video"]

        return video_tensor_long, video_tensor_short

    async def send_video_to_triton(self, video_tensor_short: torch.Tensor, video_tensor_long) -> List[float]:
        """
        Асинхронно отправляет видео тензор на Triton сервер и получает эмбеддинги.
        """
        return await asyncio.to_thread(self._send_video_to_triton, video_tensor_short, video_tensor_long)

    def _send_video_to_triton(self, video_tensor_short, video_tensor_long):

        if video_tensor_long.dim() != 5:
            video_tensor_long = video_tensor_long.unsqueeze(0)
        video_tensor_long_np = video_tensor_long.cpu().numpy().astype(np.float32)

        if video_tensor_short.dim() != 5:
            video_tensor_short = video_tensor_short.unsqueeze(0)
        video_tensor_short_np = video_tensor_short.cpu().numpy().astype(np.float32)

        input_tensor_short = grpcclient.InferInput('input__0', video_tensor_short.shape, "FP32")
        input_tensor_short.set_data_from_numpy(video_tensor_short_np)

        input_tensor_long = grpcclient.InferInput('input__1', video_tensor_long.shape, "FP32")
        input_tensor_long.set_data_from_numpy(video_tensor_long_np)

        inputs = [
            input_tensor_short,
            input_tensor_long,
        ]

        outputs = [
            grpcclient.InferRequestedOutput('output__0')
        ]
        try:
            response = self.triton_client.infer(
                model_name=self.model_name,
                inputs=inputs,
                outputs=outputs
            )
        except Exception as e:
            raise RuntimeError(f"Ошибка при обращении к Triton серверу: {e}")

        embeddings = response.as_numpy('output__0')

        return embeddings

    async def search_nearest_vector(self, embeddings: List[float]) -> Tuple[bool, Optional[str]]:
        """
        Асинхронно выполняет поиск ближайшего вектора для определения дубликата.
        """
        # Если поиск не является блокирующей операцией, можно оставить его синхронным
        # В противном случае, используйте asyncio.to_thread
        return await asyncio.to_thread(self._search_nearest_vector_blocking, embeddings)

    def _search_nearest_vector_blocking(self, embeddings: List[float]) -> Tuple[bool, Optional[str]]:
        # Реализация логики поиска ближайшего вектора с использованием FAISS или другой библиотеки
        # Пример заглушки:
        is_duplicate = True  # Замените на реальную логику
        duplicate_video_id = '23fac2f2-7f00-48cb-b3ac-aac8caa3b6b4' if is_duplicate else None
        return is_duplicate, duplicate_video_id

    async def check_video_duplicate(self, link_request: VideoLinkRequest) -> VideoLinkResponse:
        """
        Асинхронно проверяет, является ли видео дубликатом.

        :param link_request: Запрос с ссылкой на видео
        :return: Ответ с информацией о дубликате
        """
        try:
            print('ЗАПРОС ПОШЕЛ ')
            # Обработка видео URL в тензоры
            video_tensor_long, video_tensor_short = await self.video_url_to_tensor(str(link_request.link))


            # Отправка тензоров видео на сервер Triton для получения эмбеддингов
            embeddings = await self.send_video_to_triton(video_tensor_short, video_tensor_long)

            # Поиск дубликатов с использованием эмбеддингов
            is_duplicate, duplicate_video_id = await self.search_nearest_vector(embeddings)

            # Возврат результата
            return VideoLinkResponse(
                is_duplicate=is_duplicate,
                duplicate_for=duplicate_video_id
            )
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except RuntimeError as re:
            raise HTTPException(status_code=500, detail=str(re))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Неизвестная ошибка: {e}")

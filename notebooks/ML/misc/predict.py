import faiss
import numpy
import pandas


def predict(faiss_index, normalized_embeddings, id_to_uuid, metadata, top_k=2):
    distances, indices = faiss_index.search(normalized_embeddings, top_k)

    y_score = numpy.clip(distances[:,1], 0.0, 1.0)

    processed_metadata = metadata.loc[id_to_uuid]
    processed_metadata["uuid_duplicate_candidate"] = id_to_uuid[indices[:,1]]
    processed_metadata = pandas.merge(processed_metadata, processed_metadata[["created"]], left_on="uuid_duplicate_candidate", right_index=True, suffixes=("", "_duplicate_candidate"))
    processed_metadata["is_duplicate_candidate_older"] = (processed_metadata["created_duplicate_candidate"] <= processed_metadata["created"])

    y_score *= processed_metadata["is_duplicate_candidate_older"].to_numpy()

    return y_score, distances, indices, processed_metadata
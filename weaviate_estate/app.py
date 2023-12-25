import gradio as gr
from weaviate_estate.query import query_an_image
from minio import Minio

METADATAS = gr.State([])
MINIO_CLIENT = Minio(
    "127.0.0.1:9000",
    access_key="bigdata2023",
    secret_key="bigdata2023",
    secure=False
)
BUCKET_NAME = "real-estate-images"

def change_metadata(evt: gr.SelectData):
    print(f"You selected {evt.value} at {evt.index} from {evt.target}")
    print(len(METADATAS))
    return METADATAS[evt.index]

def postprocess(image):
    images, metadatas = query_an_image(image)
    global METADATAS 
    METADATAS = metadatas
    return images

def get_minio_data(id):
    all_objects = MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=id)
    images = []
    print(id)
    for i in range(3):
        try:
            MINIO_CLIENT.fget_object(BUCKET_NAME, f"{id}/{i}.png", f"/tmp/{i}.png")
        except:
            continue
        images.append(f"/tmp/{i}.png")
    return gr.Gallery(images)


def launch():
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                image = gr.Image()
                query_btn = gr.Button("Query")
            with gr.Column():
                result_image_show = gr.Gallery()
                id = gr.Label(label="ID")
                title = gr.Textbox(label="Title")
                price = gr.Textbox(label="Price")
                show_btn = gr.Button("Show details")
        with gr.Row():
            detail_query = gr.Gallery()
        query_btn.click(postprocess, inputs=[image], outputs=[result_image_show])
        result_image_show.select(change_metadata, None, outputs=[title, price, id])
        show_btn.click(get_minio_data, inputs=[id], outputs=detail_query)
    return demo

if __name__ == "__main__":
    demo = launch()
    demo.queue().launch(share=False)


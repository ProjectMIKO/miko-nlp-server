import io
import ffmpeg


def convert_to_wav(file_content):
    input_stream = io.BytesIO(file_content)
    output_stream = io.BytesIO()

    process = (
        ffmpeg
        .input('pipe:0')
        .output('pipe:1', format='wav')
        .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    )

    out, err = process.communicate(input=input_stream.read())
    output_stream.write(out)
    output_stream.seek(0)

    return output_stream

# PyScribe-AI

PyScribe-AI is a Python application that turns spoken audio into clean, structured, AI-generated notes. It is designed to help users transcribe recordings, summarize key points, and turn conversations into usable documentation in minutes.

Whether you are journaling meetings, recording classroom lectures, capturing interviews, or organizing personal voice notes, PyScribe-AI makes it easy to convert raw audio into readable, actionable content.

## Features

- Audio transcription from uploaded files
- AI-powered summary generation
- Clean, readable output in Markdown or plain text
- Support for multiple speakers and conversation structure
- Easy-to-use Python interface for local or cloud-based AI backends
- Export-ready notes for personal, academic, or business use
- Extensible architecture for adding more AI workflows

## Why this project exists

Many voice recordings are hard to review, search, or reuse. PyScribe-AI solves that by combining speech recognition and language processing in one workflow so users can focus on the content instead of manual transcription.

## Tech Stack

- Python
- Speech-to-text / transcription backend
- AI summarization pipeline
- Optional API integrations for LLM services
- Markdown export support

## Project Goals

- Make transcription simpler and faster
- Turn recordings into useful notes automatically
- Keep the workflow accessible for everyday users
- Provide a clean foundation for future AI features

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/PyScribe-AI.git
   cd PyScribe-AI
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows:

   ```powershell
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables if the app uses an AI provider or API key:

   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

   Or add them to a `.env` file if your project uses one.

## Usage

Start the app:

```bash
python app.py
```

If your project includes a web or GUI interface, use the app's launch command instead, for example:

```bash
streamlit run app.py
```

Then:

- Upload or select an audio file
- Run transcription
- Generate notes or summaries
- Review and export the results

## Example Workflow

```text
Audio input -> Speech recognition -> Text cleanup -> AI summary -> Final notes
```

## Configuration

Depending on your setup, you may need to configure:

- Speech recognition backend
- AI model/provider
- Output format (Markdown, TXT, JSON, etc.)
- Audio input location
- Environment variables or config file settings

## Folder Structure

```text
PyScribe-AI/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── src/
│   ├── transcriber.py
│   ├── summarizer.py
│   ├── utils.py
│   └── export.py
├── data/
│   └── sample_audio/
└── output/
    └── notes/
```

## Roadmap

- Improve transcription accuracy
- Add support for more file formats
- Add speaker segmentation and labeling
- Improve summarization quality
- Add export to DOCX/PDF/Markdown
- Create a cleaner web or desktop UI

## License

This project is provided as-is for educational and personal use. Add a license file if you plan to distribute or publish it publicly.

## Contributing

Contributions are welcome. If you want to improve the app, open an issue or submit a pull request with a clear description of the change.

## Contact

If you want to reach out about this project, use the repository's discussion or issue tracker.

---

Built with Python and AI-powered transcription workflows.

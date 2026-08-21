# Forum Project

This project involves firmware for data collection, feature extraction, and machine learning classification for pilot data analysis.

## Project Structure
- `firmware/`: Embedded software for data collection and preprocessing
- `host_scripts/`: Python scripts for data analysis, model training, and evaluation
- `Datasets/`: Raw and processed datasets
- `analysis/`: Analytical scripts and results
- `docs/`: Documentation
- `images/`: Diagrams and visual assets
- `tools/`: Utility tools
- `sessions/`: Session logs or temporary files

## Key Technologies
- Python (host_scripts)
- Embedded C/C++ (firmware, inferred from file extensions and context)
- Machine Learning (scikit-learn based on file names: logreg.py, model.py, scaler.py)
- Signal Processing (FFT via fft.py)
- Data Collection (RawDataCollection.py, collect_pilot.py)
- Feature Extraction (feature_extract.py)
- Model Training (train_classifier.py)
- Model Inference (embedded_main.py)

## Development Workflow
1. Data collection via firmware
2. Pilot data collection and labeling
3. Feature extraction and preprocessing
4. Model training and evaluation
5. Model deployment to embedded system

## Windows-Specific Notes
- Project configured for Windows development environment
- Uses .venv virtual environment
- SolidWorks setup executable present for CAD work
- MATLAB-colab integration indicated by colab.py

## Automation Opportunities
- Hooks for automatic linting/formatting on Python file saves
- Skills for generating ML pipeline boilerplate
- MCP servers for documentation lookup (context7) and hardware debugging
- Subagents for firmware review and ML code analysis
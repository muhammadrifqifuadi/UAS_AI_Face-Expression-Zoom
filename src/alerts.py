def check_confusion_alert(detected_expressions):
    confused_labels = ['Angry', 'Fear', 'Sad']
    total_faces = len(detected_expressions)
    confused_count = sum(1 for exp in detected_expressions if exp in confused_labels)

    if total_faces > 0 and (confused_count / total_faces) >= 0.5:
        return True
    return False

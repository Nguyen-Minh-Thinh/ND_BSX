import { useState } from 'react';

export default function UploadZone({ onFileSelect, isDisabled, previewSrc }) {
  const [dragOver, setDragOver] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      onFileSelect(droppedFile);
    } else {
      alert('Vui lòng chọn ảnh hợp lệ (.jpg, .jpeg, .png)');
    }
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.type.startsWith('image/')) {
      onFileSelect(selected);
    } else {
      alert('Vui lòng chọn ảnh hợp lệ (.jpg, .jpeg, .png)');
    }
  };

  return (
    <div
      className={`upload-zone mb-4 ${dragOver ? 'dragover' : ''}`}
      id="dropZone"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="text-center p-4 border rounded-3 position-relative">
      {!previewSrc && (
        <div className="upload-content">
            <i className="bi bi-cloud-upload display-4"></i>
            <p className="mb-2">Kéo và thả ảnh hoặc click để tải lên</p>
            <p className="text-muted small mb-3">Hỗ trợ định dạng: .jpg, .jpeg, .png</p>
            <label className="btn btn-primary mb-0" htmlFor="fileInput">Duyệt tập tin</label>
            <input
            type="file"
            id="fileInput"
            className="d-none"
            accept=".jpg,.jpeg,.png"
            disabled={isDisabled}
            onChange={handleFileChange}
            />
        </div>
        )}

        {previewSrc && (
          <div className="mt-4">
            <img
              src={previewSrc}
              alt="Xem trước"
              className="preview-image rounded shadow-sm"
              style={{ maxHeight: '400px', objectFit: 'cover', width: '100%' }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

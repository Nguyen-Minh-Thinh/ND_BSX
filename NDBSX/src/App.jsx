import { useState } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import UploadZone from './components/UploadZone';
import RecognitionResult from './components/RecognitionResult';
import Footer from './components/Footer';

function App() {
  const [file, setFile] = useState(null);
  const [plate, setPlate] = useState('');
  const [type, setType] = useState('');
  const [image, setImage] = useState('');
  const [imageSrc, setImageSrc] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile.type.startsWith('image/')) {
      alert('Vui lòng chọn file ảnh (.jpg, .jpeg, .png)');
      return;
    }
    setFile(selectedFile);
    const reader = new FileReader();
    reader.onload = () => setImage(reader.result);
    reader.readAsDataURL(selectedFile);
  };

  const recognize = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      const res = await axios.post('http://localhost:8000/process_license_plate', formData);
      setPlate(res.data.license_plate || 'Không xác định');
      setType(res.data.vehicle_type || 'Không xác định');
      setImageSrc(`http://localhost:8000${res.data.processed_image}`|| '');
    } catch (error) {
      alert('Lỗi nhận dạng biển số');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <HeroSection />
      <div className="container py-4">
        <div className="card shadow-lg recognition-card mb-4">
          <div className="card-body p-4 text-center">
            <h3 className="mb-4">Quét biển số xe</h3>
            <UploadZone
              onFileSelect={handleFileSelect}
              isDisabled={loading}
              previewSrc={image}
            />
            {plate && <RecognitionResult plate={plate} type={type} imageSrc={imageSrc} />}
            <div className="text-center">
              <button className="btn btn-primary btn-lg" disabled={!file || loading} onClick={recognize}>
                {loading ? 'Đang xử lý...' : 'Nhận dạng'}
              </button>
              <button className="btn btn-outline-secondary btn-lg ms-2" onClick={() => {
                setFile(null); setPlate(''); setType(''); setImage('');
              }}>
                Xóa
              </button>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
}

export default App;

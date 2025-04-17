export default function RecognitionResult({ plate, type, imageSrc }) {
    return (
      <div className="recognition-result mb-4">
        <div className="card border-success">
          <div className="card-body">
            <h5 className="card-title">Kết quả nhận diện</h5>
            <div className="row g-3">
              <div className="col-md-4">
                <p className="mb-2"><strong>Biển số xe:</strong></p>
                <h3 className="plate-number">{plate}</h3>
              </div>
              <div className="col-md-4">
                <p className="mb-2"><strong>Loại xe:</strong></p>
                <p className="vehicle-type mb-0">{type}</p>
              </div>
            </div>
            {imageSrc && <img src={imageSrc} className="img-fluid mb-3" alt="Kết quả nhận diện" />}
          </div>
        </div>
      </div>
    );
  }
  
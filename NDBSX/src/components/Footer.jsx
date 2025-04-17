export default function Footer() {
    return (
      <footer className="bg-dark text-white py-4 mt-5">
        <div className="container">
          <div className="row">
            <div className="col-md-6">
              <h5>Smart LPR System</h5>
              <p>Hệ thống nhận diện biển số tiên tiến sử dụng AI</p>
            </div>
            <div className="col-md-3">
              <h5>Liên kết nhanh</h5>
              <ul className="list-unstyled">
                <li><a href="#" className="text-white">Trang chủ</a></li>
                <li><a href="#history" className="text-white">Lịch sử</a></li>
                <li><a href="#analytics" className="text-white">Thống kê</a></li>
              </ul>
            </div>
            <div className="col-md-3">
              <h5>Liên hệ</h5>
              <ul className="list-unstyled">
                <li><i className="bi bi-envelope me-2"></i>support@lpr.com</li>
                <li><i className="bi bi-telephone me-2"></i>1-800-LPR-SCAN</li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    );
  }
  
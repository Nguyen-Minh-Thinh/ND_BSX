export default function Navbar() {
    return (
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
        <div className="container">
          <a className="navbar-brand" href="#">
            <i className="bi bi-camera-fill me-2"></i>Smart LPR System
          </a>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item"><a className="nav-link active" href="#">Trang chủ</a></li>
              <li className="nav-item"><a className="nav-link" href="#analytics">Thống kê</a></li>
            </ul>
          </div>
        </div>
      </nav>
    );
  }
  
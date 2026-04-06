import { useEffect, useState } from "react";
import { TagCross } from "iconsax-react";

const ContainerView = ({ showPopup, closePopup, imageView }) => {
  const [loading, setLoading] = useState(false);
  const [containerImage, setContainerImage] = useState(null);

  // useEffect(() => {
  //   setLoading(true);
  //   setTimeout(() => {
  //     setContainerImage(imageView);
  //     setLoading(false);
  //   }, 1000); // Simulating loading time
  // })

  if (!showPopup) return null;
  return (
    <div className="d-fixed">
      <div className="popup-container active p-absolute">
        <div className="popup-box">
          <div className="d-flex justify-content-between align-items-start">
            <div>
              <h2 className="text-lg font-bold mb-1 f-18">3D Container View</h2>
              <p className="p-0 m-0 mb-2 f-12">3D View Pallet Arrangements</p>
            </div>
            <div className="d-flex justify-content-end align-items-center">
              <button
                className="btn d-flex justify-content-center align-items-center bor-15 bg-btn-custom-danger"
                onClick={closePopup}
              >
                <TagCross size="24" color="red" />
              </button>
            </div>
          </div>

          {loading ? (
            <div className="text-center p-4">
              <div className="animate-spin rounded-full h-10 w-10 border-t-4 border-blue-500"></div>
              <p className="mt-2">Loading...</p>
            </div>
          ) : (
            <div className="W-100 bor-10 overflow-hidden h-75 mt-2">
              <img
                className="img-fluid"
                src={imageView}
                alt="3D View"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ContainerView;

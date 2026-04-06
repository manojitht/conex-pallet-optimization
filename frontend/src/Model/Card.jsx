import { useState, useEffect } from "react";
import boxImge1 from "../assets/img/box1.png";
import boxImge2 from "../assets/img/box2.png";
import boxImge3 from "../assets/img/box3.png";
//import { BagCross } from "iconsax-react";

const Card = ({ id, cargo, dimensions, weight, quantity, onDelete }) => {
  const getPalletImage = () => {
    switch (dimensions) {
      case "4 x 3 x 6":
        return boxImge1; 
      case "4 x 3 x 3":
        return boxImge3; 
      case "4 x 3 x 2":
        return boxImge2; 
    }
  };

  const getPalletName = () => {
    switch (dimensions) {
      case "4 x 3 x 6":
        return '4ft x 3ft x 6ft'; 
      case "4 x 3 x 3":
        return '4ft x 3ft x 3ft'; 
      case "4 x 3 x 2":
        return '4ft x 3ft x 2ft'; 
    }
  };

  const getPalletLabel = () => {
    switch (dimensions) {
      case "4 x 3 x 6":
        return "Full Pallet";
      case "4 x 3 x 3":
        return "Half Pallet";
      case "4 x 3 x 2":
        return "Quarter Pallet";
    }
  };

  return (
    <div className="form-control p-3 border-0 shadow">
      <div className="d-flex justify-content-between align-items-start">
        <div className="mb-2">
          <h5 className="p-0 m-0 f-14 mb-1">{cargo}</h5>
          <p className="p-0 m-0 form-text f-12">
            ID: <span className="m-0 text-muted">PLT{id}</span>
          </p>
        </div>
        <div className="mb-2">
          {/* <button
            className="btn d-flex justify-content-center align-items-center bor-15 bg-btn-custom-danger"
            style={{ width: "44px", height: "44px" }}
            onClick={() => onDelete(id)}
          >
            <BagCross size="24" color="red" />
          </button> */}
        </div>
      </div>

      <div className="img bor-10 overflow-h mb-2">
        <img src={getPalletImage()} alt="Pallet image" className="img-fluid" />
      </div>

      <div className="p-2 d-flex justify-content-between align-items-start bor-10 bg-light-grey px-3">
        <div className="mb-2">
          <p className="p-0 m-0 f-12 fw-bold">
            {weight} <span className="f-12 fw-bold">KG</span>
          </p>
          <p className="p-0 m-0 f-12">
            <span className="f-12 form-text">QT: </span>
            {quantity}
          </p>
        </div>
        <div className="px-1"></div>
        <div className="mb-2">
          <p className="p-0 m-0 f-14 fw-bold">{getPalletLabel()}</p>
          <p className="p-0 m-0 form-text f-12">{getPalletName()}</p>
        </div>
      </div>
    </div>
  );
};

export default Card;

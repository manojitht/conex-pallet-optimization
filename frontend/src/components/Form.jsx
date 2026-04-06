import { useState, useEffect } from "react";
import ContainerView from "./containerView";
import { Trash } from "iconsax-react";
import Card from "../Model/Card.jsx";
import axios from "axios";

const Form = () => {
  const [containerSize, setContainerSize] = useState("20ft");
  const [palletType, setPalletType] = useState("full");
  const [showPopup, setShowPopup] = useState(false);
  const [loading, setLoading] = useState(false);
  const [cargoList, setCargoList] = useState([]);
  const [lengthLimit, setLengthLimit] = useState(18); 
  const [weightLimit, setWeightLimit] = useState(48000); 
  const [imgSource, setImageSource] = useState(null); 
  const [formData, setFormData] = useState({
    length: 0,
    width: 0,
    height: 0,
    weight_limit: 0,
    pallets: [],
  });

  const palletOptions = {
    full: { dimensions: "4ft x 3ft x 6ft", weight: 2600 },
    half: { dimensions: "4ft x 3ft x 3ft", weight: 1100 },
    quarter: { dimensions: "4ft x 3ft x 2ft", weight: 550 },
  };

  const [palletDimensions, setPalletDimensions] = useState({
    length: 4,
    width: 3,
    height: 6,
  });

  const handlePalletTypeChange = (e) => {
    setPalletType(e.target.value);
    const selectedPallet = palletOptions[e.target.value];
    const [length, width, height] = selectedPallet.dimensions
      .split(" x ")
      .map((dim) => parseFloat(dim)); 
    setPalletDimensions({ length, width, height });
  };

  const addPallet = () => {
    const newCargo = {
      id: cargoList.length + 1,
      cargo: "",
      length: palletDimensions.length,
      width: palletDimensions.width,
      height: palletDimensions.height,
      weight: "",
      quantity: "",
    };

    setCargoList([...cargoList, newCargo]);
  };

  const deletePallet = (id) => {
    setCargoList(cargoList.filter((cargo) => cargo.id !== id));
  };

  const generate3DView = () => {
    setShowPopup(true);
    setLoading(true);

    // Format cargo data before setting formData
    const formattedCargoList = formatCargoData(cargoList);

    // Update formData with the latest cargo list
    const updatedFormData = {
      length: lengthLimit,
      width: 7,
      height: 7,
      weight_limit: weightLimit,
      pallets: formattedCargoList,
    };

    setFormData(updatedFormData);
    postData(updatedFormData); 
  };

  const formatCargoData = (cargoList) => {
    return cargoList.map((cargo) => ({
      pallet_id: `${palletType}-${cargo.id}`, 
      length: parseFloat(cargo.length),
      width: parseFloat(cargo.width),
      height: parseFloat(cargo.height),
      weight: parseFloat(cargo.weight) || 0, 
      quantity: parseInt(cargo.quantity) || 0, 
    }));
  };

  const postData = async (formData) => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/v1/load_pallets",
        formData
      );
      console.log("Response from server:", response.data);

      
      setImageSource(response.data.visualization);
    } catch (error) {
      console.error("Error posting data:", error);
    } finally {
      setLoading(false); 
    }
  };

  const closePopup = () => {
    setShowPopup(false);
  };

  const handleInputChange = (id, field, value) => {
    setCargoList(
      cargoList.map((cargo) =>
        cargo.id === id
          ? {
              ...cargo,
              [field]: field === "quantity" || field === "weight" ? parseFloat(value) || 0 : value,
            }
          : cargo
      )
    );
  };

  useEffect(() => {
    console.log("Updated formData:", formData); 
  }, [formData]);

  return (
    <div className="container p-4 mt-3">
      <div className="row">
        {/* Left Section - Form */}
        <div
          className={
            cargoList.length > 0
              ? "col-md-6"
              : "d-flex justify-content-center align-items-center"
          }
        >
          <div
            className={`form-control shadow border-0 p-4 make-me-sticky ${
              cargoList.length === 0 ? "w-50" : ""
            }`}
          >
            <div className="mb-3 mt-2">
              <h4 className="p-0 m-0">Pallet Optimization</h4>
            </div>

            <div className="mb-3">
              <label className="block font-medium f-12 mb-1">Select Container Size:</label>
              <select
                className="custom-select f-14"
                value={containerSize}
                onChange={(e) => {
                  const selectedValue = e.target.value;
                  setContainerSize(selectedValue);
                  setLengthLimit(selectedValue === "20ft" ? 18 : 39);
                }}
              >
                <option value="20ft">20 ft (48,000 lbs)</option>
                <option value="40ft">40 ft (65,350 lbs)</option>
              </select>
            </div>

            <div className="d-flex flex-column align-items-end">
              <button
                className="btn btn-primary f-14 py-2 add-btn-custom"
                onClick={addPallet}
              >
                Add Cargo
              </button>
              <p className="mt-2 text-muted f-12">
                * All weights are in kilograms (kgs), and dimensions are in feet (ft).
              </p>
            </div>

            <div className="mb-3">
              <label className="label f-12 mb-1">Select Pallet Type:</label>
              <select
                className="custom-select f-14"
                value={palletType}
                onChange={handlePalletTypeChange}
              >
                <option value="full">Full Pallet</option>
                <option value="half">Half Pallet</option>
                <option value="quarter">Quarter Pallet</option>
              </select>
            </div>

            <div className="mt-4">
              <table className="table table-bordered">
                <thead>
                  <tr>
                    <th className="f-12 poppins-regular">Cargo</th>
                    <th className="f-12 poppins-regular">Length</th>
                    <th className="f-12 poppins-regular">Width</th>
                    <th className="f-12 poppins-regular">Height</th>
                    <th className="f-12 poppins-regular">Weight</th>
                    <th className="f-12 poppins-regular">Quantity</th>
                    <th className={cargoList.length === 0 ? "d-none" : "f-12 poppins-regular"}>
                      {cargoList.length > 0 ? "Action" : ""}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {cargoList.length > 0 ? (
                    cargoList.map((cargo) => (
                      <tr key={cargo.id}>
                        <td>
                          <div className="d-flex justify-content-center align-items-center pt-1">
                            <input
                              type="text"
                              className="form-control"
                              value={cargo.cargo}
                              onChange={(e) =>
                                handleInputChange(cargo.id, "cargo", e.target.value)
                              }
                            />
                          </div>
                        </td>
                        <td>
                          <div className="d-flex justify-content-center align-items-center pt-2">
                            <p className="f-14">{cargo.length}ft</p>
                          </div>
                        </td>
                        <td>
                          <div className="d-flex justify-content-center align-items-center pt-2">
                            <p className="f-14">{cargo.width}ft</p>
                          </div>
                        </td>
                        <td>
                          <div className="d-flex justify-content-center align-items-center pt-2">
                            <p className="f-14">{cargo.height}ft</p>
                          </div>
                        </td>
                        <td>
                          <div className="d-flex justify-content-center align-items-center pt-1">
                            <input
                              min="0"
                              className="form-control"
                              value={cargo.weight}
                              onChange={(e) =>
                                handleInputChange(cargo.id, "weight", e.target.value)
                              }
                            />
                          </div>
                        </td>
                        <td>
                          <div className="d-flex justify-content-center align-items-center pt-1">
                            <input
                              className="form-control"
                              value={cargo.quantity}
                              onChange={(e) =>
                                handleInputChange(cargo.id, "quantity", e.target.value)
                              }
                            />
                          </div>
                        </td>
                        <td>
                          <button
                            className="btn d-flex justify-content-center align-items-center bor-15 bg-btn-custom-danger"
                            onClick={() => deletePallet(cargo.id)}
                          >
                            <Trash size="18" color="#f47373" variant="Bold" />
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="text-center f-14 poppins-regular">
                        No Cargo Added
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="d-flex justify-content-end align-items-center mt-3">
              <button
                className="custom-button bg-light-green"
                onClick={generate3DView}
              >
                3D View
              </button>
            </div>
          </div>
        </div>

        {/* Right Section - Card Display */}
        <div className={cargoList.length > 0 ? "col-md-6" : "d-none"}>
          <div className="mt-4">
            <h4 className="p-0 m-0 pt-2">Store Palletizer</h4>
          </div>
          <div
            className="container-fluid bg-transparent my-4"
            style={{ position: "relative" }}
          >
            <div className="row row-cols-1 row-cols-xs-2 row-cols-sm-2 row-cols-lg-2 g-3">
              {cargoList.map((cargo) =>
                cargo.cargo && cargo.weight ? (
                  <div key={cargo.id}>
                    <Card
                      id={cargo.id}
                      cargo={cargo.cargo}
                      dimensions={`${cargo.length} x ${cargo.width} x ${cargo.height}`}
                      weight={cargo.weight}
                      quantity={cargo.quantity}
                    />
                  </div>
                ) : null
              )}
            </div>
          </div>
        </div>
      </div>

      <ContainerView
        showPopup={showPopup}
        loading={loading}
        closePopup={closePopup}
        imageView={imgSource} 
      />
    </div>
  );
};

export default Form;
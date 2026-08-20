export interface PredictionRequest {
  location: string;
  bhk: number;
  carpet_area_sqft: number;
  floor_num: number;
  bathroom: number;
  balcony: number;
  car_parking: number;
  furnishing: "Furnished" | "Semi-Furnished" | "Unfurnished";
  transaction: "New Property" | "Resale";
  ownership: string;
  facing: string;
}

export interface PredictionResponse {
  predicted_price: number;
}

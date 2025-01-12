from datetime import datetime
from typing import Optional, Literal, Dict
from pydantic import BaseModel, EmailStr, validator, root_validator
import joblib
import numpy as np

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict


class TokenData(BaseModel):
    email: Optional[str] = None
    uid: Optional[int] = None


class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    uid: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class RegisterResponse(BaseModel):
    message: str
    success: bool

# Schémas pour les sessions
class SessionBase(BaseModel):
    session_name: str

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: int
    user_uid: int
    created_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    session_id: int
    message: Dict[str, float]
    model_type: Literal["classification", "regression"]
    algorithm: str

    # @validator('algorithm')
    # def validate_algorithm(cls, v, values):
    #     valid_algorithms = {
    #         "classification": ["decision_tree", "bagging", "adaboost", "random_forest", "svm"],
    #         "regression": ["decision_tree", "bagging", "random_forest", "svm", "ridge"]
    #     }
    #     if v not in valid_algorithms[values['model_type']]:
    #         raise ValueError(f"Invalid algorithm for {values['model_type']}")
    #     return v
    #
    #
    # @validator('message')
    # def validate_features(cls, v, values):
    #     valid_features = {
    #         "classification": {
    #             "decision_tree": ["Vn", "ZCR", "SF", "CGS", "CS"],
    #             "bagging": ["Vn", "ZCR", "SF", "CGS"],
    #             "adaboost": ["Vn", "ZCR", "SF", "CGS", "CS"],
    #             "random_forest": ["Vn", "ZCR", "SF", "CGS", "CS"],
    #
    #         },
    #         "regression": {
    #             "decision_tree": ["Vn", "ZCR", "CGS", "SNR"],
    #             "bagging": ["Vn", "ZCR", "CGS", "SNR"],
    #             "random_forest": ["Vn", "ZCR", "CGS", "SNR"],
    #             "svm": [ "ZCR", "Vn", "SNR", "SF" ],
    #             "ridge": [ "ZCR", "Vn", "SNR", "CGS" ]
    #         }
    #     }
    #     algorithm = values.get('algorithm')
    #     model_type = values.get('model_type')
    #
    #     if not all(feature in valid_features[model_type][algorithm] for feature in v):
    #         raise ValueError(f"Invalid features for {model_type} {algorithm}")
    #     return v



    # Utiliser root_validator pour valider tous les champs ensemble
    @root_validator(pre=True)
    def validate_all_fields(cls, values):
        model_type = values.get('model_type')
        algorithm = values.get('algorithm')
        message = values.get('message')

        if not all([model_type, algorithm, message]):
            raise ValueError("model_type, algorithm, and message are required")

        valid_algorithms = {
            "classification": ["decision_tree", "bagging", "adaboost", "random_forest"],
            "regression": ["decision_tree", "bagging", "random_forest", "svm", "ridge"]
        }

        if model_type not in valid_algorithms:
            raise ValueError(f"Invalid model_type: {model_type}")

        if algorithm not in valid_algorithms[model_type]:
            raise ValueError(f"Invalid algorithm {algorithm} for model_type {model_type}")

        valid_features = {
            "classification": {
                "decision_tree": ["Vn", "ZCR", "SF", "CGS", "CS"],
                "bagging": ["Vn", "ZCR", "SF", "CGS"],
                "adaboost": ["Vn", "ZCR", "SF", "CGS", "CS"],
                "random_forest": ["Vn", "ZCR", "SF", "CGS", "CS"]
            },
            "regression": {
                "decision_tree": ["Vn", "ZCR", "CGS", "SNR"],
                "bagging": ["Vn", "ZCR", "CGS", "SNR"],
                "random_forest": ["Vn", "ZCR", "CGS", "SNR"],
                "svm": ["ZCR", "Vn", "SNR", "SF"],
                "ridge": ["ZCR", "Vn", "SNR", "CGS"]
            }
        }

        expected_features = set(valid_features[model_type][algorithm])
        provided_features = set(message.keys())

        if expected_features != provided_features:
            missing = expected_features - provided_features
            extra = provided_features - expected_features
            error_msg = []
            if missing:
                error_msg.append(f"Missing features: {list(missing)}")
            if extra:
                error_msg.append(f"Extra features: {list(extra)}")
            raise ValueError(", ".join(error_msg))

        return values


class MessageResponse(BaseModel):
    id: int
    session_id: int
    message: Dict[str, float]
    sender: str
    model_type: str
    algorithm: str
    created_at: datetime
    prediction: float

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


ML_MODELS = {
    "classification": {
        "decision_tree": joblib.load("src/app/models/classification/decision_tree_model.pkl"),
        "bagging": joblib.load("src/app/models/classification/bagging_model.pkl"),
        "adaboost": joblib.load("src/app/models/classification/adaboost_model.pkl"),
        "random_forest": joblib.load("src/app/models/classification/linear_svm_model.pkl"),

    },
    "regression": {
        "decision_tree": joblib.load("src/app/models/regression/arbre_quality_predictor.joblib"),
        "bagging": joblib.load("src/app/models/regression/bagging_quality_predictor.joblib"),
        "random_forest": joblib.load("src/app/models/regression/random_forest_quality_predictor.joblib"),
        "svm": joblib.load("src/app/models/regression/svm_nonlin_quality_predictor.joblib"),
        "ridge": joblib.load("src/app/models/regression/ridge_quality_predictor.joblib")
    }
}


def prepare_features(features: Dict[str, float], model_type: str, algorithm: str) -> np.ndarray:
    """Prépare les features dans l'ordre attendu par le modèle."""
    feature_order = {
        "classification": {
            "decision_tree": ["Vn", "ZCR", "SF", "CGS", "CS"],
            "bagging": ["Vn", "ZCR", "SF", "CGS"],
            "adaboost": ["Vn", "ZCR", "SF", "CGS", "CS"],
            "random_forest": ["Vn", "ZCR", "SF", "CGS", "CS"],

        },
        "regression": {
            "decision_tree": ["Vn", "ZCR", "CGS", "SNR"],
            "bagging": ["Vn", "ZCR", "CGS", "SNR"],
            "random_forest": ["Vn", "ZCR", "CGS", "SNR"],
            "svm": [ "ZCR", "Vn", "SNR", "SF" ],
            "ridge": [ "ZCR", "Vn", "SNR", "CGS" ]
        }
    }

    ordered_features = [features[f] for f in feature_order[model_type][algorithm]]
    return np.array(ordered_features).reshape(1, -1)




# class TargetBase(BaseModel):
#     "classe"
#     "Moy. DMOS"


# # Schémas pour les messages
# class MessageBase(BaseModel):
#     message: str


# class MessageCreate(MessageBase):
#     session_id: int


# class MessageResponse(MessageBase):
#     id: int
#     session_id: int
#     sender: str
#     created_at: datetime
#
#     class Config:
#         from_attributes = True

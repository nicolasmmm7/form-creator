import React from "react";
import { useNavigate } from "react-router-dom";

const UserAvatar = ({ src, alt, size = 40 }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate("/profile");
  };

  return (
    <img
      src={src || "/default-avatar.png"}
      alt={alt || "Avatar"}
      onClick={handleClick}
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        cursor: "pointer",
        objectFit: "cover",
      }}
    />
  );
};

export default UserAvatar;
const express = require("express");
const morgan = require("morgan");
const path = require("path");
const routes = require("./routes");

const app = express();
const PORT = process.env.PORT || 3000;

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

app.use(morgan("dev"));
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, "..", "public")));

app.use("/", routes);

app.listen(PORT, () => {
  console.log(`PriceWatch frontend listening on port ${PORT}`);
});

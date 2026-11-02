
const test = require("node:test");
const assert = require("node:assert/strict");
const { add } = require("../src/index");

test("add returns the sum of two numbers", () => {
  assert.equal(add(2, 3), 5);
});

test("add supports negative numbers", () => {
  assert.equal(add(-2, 3), 1);
});

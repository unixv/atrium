import assert from "node:assert/strict";
import test from "node:test";
import { movementDelta } from "../src/game/keyboard.ts";

test("maps arrow keys to adjacent tiles", () => {
  assert.deepEqual(movementDelta("ArrowUp"), { x: 0, y: -1 });
  assert.deepEqual(movementDelta("ArrowDown"), { x: 0, y: 1 });
  assert.deepEqual(movementDelta("ArrowLeft"), { x: -1, y: 0 });
  assert.deepEqual(movementDelta("ArrowRight"), { x: 1, y: 0 });
});

test("maps WASD case-insensitively", () => {
  assert.deepEqual(movementDelta("w"), { x: 0, y: -1 });
  assert.deepEqual(movementDelta("A"), { x: -1, y: 0 });
  assert.deepEqual(movementDelta("S"), { x: 0, y: 1 });
  assert.deepEqual(movementDelta("d"), { x: 1, y: 0 });
});

test("ignores unrelated keys", () => {
  assert.equal(movementDelta("Enter"), undefined);
  assert.equal(movementDelta("q"), undefined);
});

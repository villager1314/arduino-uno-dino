// Arduino Uno Dino: ATmega328P runs gameplay; the PC only renders it.
const float GROUND_Y = 357.0f;
const float GRAVITY = 1450.0f;
const float JUMP_SPEED = 570.0f;
const float DINO_X = 120.0f;
const float DINO_W = 58.0f;

float dinoY = GROUND_Y, velocityY = 0;
struct Obstacle { float x; byte type; byte height; bool fired; };
// type: 0 cactus, 1 bird, 2 stickman, 3 tank, 4 poison pool
Obstacle obstacles[2] = {{850, 0, 52, false}, {1260, 2, 0, false}};
float obstacleSpeed = 330;
bool jumpDown = false, jumpWasDown = false, gameOver = false;
bool paused = false;
byte shieldCount = 0;
float teaX = -100.0f;
int teaY = 318;
unsigned long nextTeaScore = 90;
float planeX = -150.0f, bulletX = -100.0f;
int bulletY = 360;
bool planeFired = false;
unsigned long nextPlaneScore = 120;
float enemyShotX = -100.0f;
int enemyShotY = 370;
byte enemyShotType = 0;
byte meteorPhase = 0;
float meteorX = 500, meteorY = -60;
unsigned long meteorPhaseStarted = 0, nextMeteorScore = 170;
unsigned long score = 0, bestScore = 0, distanceRun = 0;
unsigned long lastStepUs, lastReportMs, randomState = 2463534242UL;
char lineBuffer[24];
byte lineLength = 0;

unsigned long nextRandom() {
  randomState ^= randomState << 13;
  randomState ^= randomState >> 17;
  randomState ^= randomState << 5;
  return randomState;
}

void newObstacle(byte index) {
  byte other = 1 - index;
  float anchor = max(960.0f, obstacles[other].x);
  // Preserve at least about one second between hazards at every speed.
  float safeGap = obstacleSpeed * 0.95f + 140.0f;
  obstacles[index].x = anchor + safeGap + (nextRandom() % 201);
  unsigned long roll = nextRandom() % 100;
  if (roll < 32) obstacles[index].type = 0;
  else if (roll < 50) obstacles[index].type = 1;
  else if (roll < 72) obstacles[index].type = 2;
  else if (roll < 88) obstacles[index].type = 3;
  else obstacles[index].type = 4;
  obstacles[index].height = 42 + (nextRandom() % 29);
  obstacles[index].fired = false;
}

void restartGame() {
  dinoY = GROUND_Y; velocityY = 0; obstacleSpeed = 330;
  score = 0; distanceRun = 0; gameOver = false;
  shieldCount = 0; teaX = -100; teaY = 318; nextTeaScore = 90;
  planeX = -150; bulletX = -100; planeFired = false; nextPlaneScore = 120;
  enemyShotX = -100; enemyShotY = 370; enemyShotType = 0;
  meteorPhase = 0; meteorX = 500; meteorY = -60; nextMeteorScore = 170;
  obstacles[0].x = 850; obstacles[0].type = 0; obstacles[0].height = 52; obstacles[0].fired = false;
  obstacles[1].x = 1260; obstacles[1].type = 2; obstacles[1].height = 0; obstacles[1].fired = false;
}

void parseInput(char *line) {
  int jump, reset, pauseValue;
  if (sscanf(line, "I,%d,%d,%d", &jump, &reset, &pauseValue) == 3) {
    jumpDown = jump != 0;
    paused = pauseValue != 0;
    if (reset || (gameOver && jumpDown && !jumpWasDown)) restartGame();
  }
}

void readInput() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n') {
      lineBuffer[lineLength] = '\0'; parseInput(lineBuffer); lineLength = 0;
    } else if (c != '\r' && lineLength < sizeof(lineBuffer) - 1) {
      lineBuffer[lineLength++] = c;
    }
  }
}

void updateGame(float dt) {
  if (paused) { jumpWasDown = jumpDown; return; }
  if (gameOver) { jumpWasDown = jumpDown; return; }
  bool grounded = dinoY >= GROUND_Y - 0.5f;
  if (jumpDown && !jumpWasDown && grounded) velocityY = -JUMP_SPEED;
  jumpWasDown = jumpDown;
  velocityY += GRAVITY * dt;
  dinoY += velocityY * dt;
  if (dinoY >= GROUND_Y) { dinoY = GROUND_Y; velocityY = 0; }

  for (byte i = 0; i < 2; ++i) obstacles[i].x -= obstacleSpeed * dt;
  distanceRun += (unsigned long)(obstacleSpeed * dt);
  score = distanceRun / 12;
  obstacleSpeed = 330.0f + min(360.0f, score * 0.35f);
  if (teaX < -50 && score >= nextTeaScore) {
    teaX = 1050.0f;
    teaY = (nextRandom() % 2) ? 315 : 345;
  }
  if (teaX >= -50) {
    teaX -= obstacleSpeed * dt;
    bool teaHitX = DINO_X + DINO_W > teaX && DINO_X < teaX + 31;
    bool teaHitY = dinoY + 53 > teaY && dinoY < teaY + 38;
    if (teaHitX && teaHitY) {
      if (shieldCount < 9) shieldCount++;
      teaX = -100;
      nextTeaScore = score + 180 + (nextRandom() % 180);
    } else if (teaX < -40) {
      teaX = -100;
      nextTeaScore = score + 120 + (nextRandom() % 140);
    }
  }

  if (planeX < -120 && score >= nextPlaneScore) {
    planeX = 1040; planeFired = false;
  }
  if (planeX >= -120) {
    planeX -= (210.0f + obstacleSpeed * 0.22f) * dt;
    if (!planeFired && planeX < 780) {
      float safeGap = obstacleSpeed * 0.95f + 160.0f;
      bool clearShot = (obstacles[0].x < 50 || obstacles[0].x > planeX + safeGap) &&
                       (obstacles[1].x < 50 || obstacles[1].x > planeX + safeGap) &&
                       enemyShotX < -30;
      if (clearShot) {
        planeFired = true; bulletX = planeX + 15; bulletY = 365;
      } else if (planeX < 300) {
        // Skip this shot instead of teleporting a visible obstacle.
        planeFired = true;
      }
    }
    if (planeX < -110) nextPlaneScore = score + 180 + (nextRandom() % 180);
  }
  if (bulletX >= -30) {
    bulletX -= (obstacleSpeed + 190.0f) * dt;
    bool bulletHit = DINO_X + DINO_W - 7 > bulletX && DINO_X + 7 < bulletX + 22 &&
                     dinoY + 48 > bulletY && dinoY + 7 < bulletY + 10;
    if (bulletHit) {
      bulletX = -100;
      if (shieldCount > 0) shieldCount--;
      else { gameOver = true; if (score > bestScore) bestScore = score; }
    }
  }

  // Stickmen shoot small bullets; tanks shoot larger shells. Only one ground
  // projectile may exist at a time so an unavoidable barrage cannot form.
  for (byte i = 0; i < 2; ++i) {
    byte other = 1 - i;
    float firingGap = obstacleSpeed * 0.95f + 160.0f;
    bool clearLane = obstacles[other].x < 40 || obstacles[other].x > obstacles[i].x + firingGap;
    if ((obstacles[i].type == 2 || obstacles[i].type == 3) && !obstacles[i].fired &&
        obstacles[i].x < 760 && obstacles[i].x > 330 && enemyShotX < -30 && clearLane && bulletX < -30) {
      obstacles[i].fired = true;
      enemyShotX = obstacles[i].x;
      enemyShotType = obstacles[i].type == 3 ? 1 : 0;
      enemyShotY = enemyShotType ? 374 : 368;
    }
  }
  if (enemyShotX >= -30) {
    enemyShotX -= (obstacleSpeed + (enemyShotType ? 130.0f : 210.0f)) * dt;
    float radius = enemyShotType ? 10.0f : 5.0f;
    bool enemyShotHit = DINO_X + DINO_W - 10 > enemyShotX - radius && DINO_X + 10 < enemyShotX + radius &&
                        dinoY + 47 > enemyShotY - radius && dinoY + 8 < enemyShotY + radius;
    if (enemyShotHit) {
      enemyShotX = -100;
      if (shieldCount > 0) shieldCount--;
      else { gameOver = true; if (score > bestScore) bestScore = score; }
    }
  }

  float nearestObstacle = min(obstacles[0].x, obstacles[1].x);
  if (meteorPhase == 0 && score >= nextMeteorScore && bulletX < -30 && enemyShotX < -30 && nearestObstacle > 1200) {
    meteorPhase = 1;
    // Always mark a landing point clearly ahead of the dinosaur.
    meteorX = 360 + (nextRandom() % 181);
    meteorY = -60;
    meteorPhaseStarted = millis();
  } else if (meteorPhase == 1 && millis() - meteorPhaseStarted >= 700) {
    meteorPhase = 2; meteorY = -35;
  } else if (meteorPhase == 2) {
    meteorY += (650.0f + obstacleSpeed * 0.35f) * dt;
    bool fallingHit = DINO_X + DINO_W - 5 > meteorX - 22 && DINO_X + 5 < meteorX + 22 &&
                      dinoY + 49 > meteorY - 20 && dinoY + 5 < meteorY + 20;
    if (fallingHit) {
      if (shieldCount > 0) { shieldCount--; meteorPhase = 0; nextMeteorScore = score + 170; }
      else { gameOver = true; if (score > bestScore) bestScore = score; }
    }
    if (meteorY >= 391) {
      meteorY = 391;
      meteorPhase = 3;
    }
  } else if (meteorPhase == 3) {
    // The burning impact site travels with the scrolling ground toward the dino.
    meteorX -= obstacleSpeed * dt;
    bool fireHit = DINO_X + DINO_W - 5 > meteorX - 38 && DINO_X + 5 < meteorX + 38 &&
                   dinoY + 49 > 365;
    if (fireHit) {
      if (shieldCount > 0) { shieldCount--; meteorPhase = 0; nextMeteorScore = score + 170; }
      else { gameOver = true; if (score > bestScore) bestScore = score; }
    } else if (meteorX < -50) {
      meteorPhase = 0;
      nextMeteorScore = score + 150 + (nextRandom() % 190);
    }
  }
  for (byte i = 0; i < 2; ++i) {
    if (obstacles[i].x < -75) newObstacle(i);
    float left = obstacles[i].x + 6;
    float right = obstacles[i].x + (obstacles[i].type == 3 ? 72 : (obstacles[i].type == 4 ? 90 : (obstacles[i].type == 0 ? 38 : 52)));
    float top;
    float bottom = 410.0f;
    if (obstacles[i].type == 0) top = 410.0f - obstacles[i].height;
    else if (obstacles[i].type == 1) { top = 337.0f; bottom = 365.0f; }
    else if (obstacles[i].type == 2) top = 350.0f;
    else if (obstacles[i].type == 3) top = 363.0f;
    else top = 397.0f;
    bool hitX = DINO_X + DINO_W - 12 > left && DINO_X + 12 < right;
    bool hitY = dinoY + 46.0f > top && dinoY + 8.0f < bottom;
    if (hitX && hitY) {
      bool stompable = obstacles[i].type == 2 || obstacles[i].type == 3;
      bool stomped = stompable && velocityY > 0 && dinoY + 53.0f <= top + 22.0f;
      if (stomped) {
        velocityY = -350.0f;
        newObstacle(i);
      } else if (shieldCount > 0) {
        shieldCount--;
        newObstacle(i);
      } else {
        gameOver = true;
        if (score > bestScore) bestScore = score;
      }
    }
  }
}

void updateLed() {
  if (gameOver) digitalWrite(LED_BUILTIN, (millis() / 140) % 2 ? HIGH : LOW);
  else digitalWrite(LED_BUILTIN, dinoY < GROUND_Y - 1.0f ? HIGH : LOW);
}

void reportState() {
  Serial.print(F("{\"y\":")); Serial.print(dinoY, 1);
  Serial.print(F(",\"x1\":")); Serial.print(obstacles[0].x, 1);
  Serial.print(F(",\"t1\":")); Serial.print(obstacles[0].type);
  Serial.print(F(",\"h1\":")); Serial.print(obstacles[0].height);
  Serial.print(F(",\"x2\":")); Serial.print(obstacles[1].x, 1);
  Serial.print(F(",\"t2\":")); Serial.print(obstacles[1].type);
  Serial.print(F(",\"h2\":")); Serial.print(obstacles[1].height);
  Serial.print(F(",\"tea\":")); Serial.print(teaX, 1);
  Serial.print(F(",\"teay\":")); Serial.print(teaY);
  Serial.print(F(",\"shield\":")); Serial.print(shieldCount);
  Serial.print(F(",\"plane\":")); Serial.print(planeX, 1);
  Serial.print(F(",\"bullet\":")); Serial.print(bulletX, 1);
  Serial.print(F(",\"bullety\":")); Serial.print(bulletY);
  Serial.print(F(",\"eshot\":")); Serial.print(enemyShotX, 1);
  Serial.print(F(",\"eshoty\":")); Serial.print(enemyShotY);
  Serial.print(F(",\"eshottype\":")); Serial.print(enemyShotType);
  Serial.print(F(",\"mphase\":")); Serial.print(meteorPhase);
  Serial.print(F(",\"meteorx\":")); Serial.print(meteorX, 1);
  Serial.print(F(",\"meteory\":")); Serial.print(meteorY, 1);
  Serial.print(F(",\"score\":")); Serial.print(score);
  Serial.print(F(",\"best\":")); Serial.print(bestScore);
  Serial.print(F(",\"over\":")); Serial.print(gameOver ? 1 : 0);
  Serial.print(F(",\"paused\":")); Serial.print(paused ? 1 : 0);
  Serial.print(F(",\"night\":")); Serial.print((score / 300) % 2);
  Serial.print(F(",\"distance\":")); Serial.print(distanceRun);
  Serial.println(F("}"));
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200); randomState ^= micros();
  lastStepUs = micros(); lastReportMs = millis();
}

void loop() {
  readInput();
  updateLed();
  unsigned long nowUs = micros();
  float dt = (nowUs - lastStepUs) / 1000000.0f;
  if (dt >= 0.004f) {
    if (dt > 0.04f) dt = 0.04f;
    lastStepUs = nowUs; updateGame(dt);
  }
  unsigned long nowMs = millis();
  if (nowMs - lastReportMs >= 33) { lastReportMs = nowMs; reportState(); }
}

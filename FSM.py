import time

class HandStateMachine:
    def __init__(self, transition_delay=2.0):
        self.state = "SENSING"
        self.transition_delay = transition_delay
        self.condition_start = None
        self.pending_state = None

    def _reset_transition(self):
        self.condition_start = None
        self.pending_state = None

    # === Basic gesture helpers ===
    def is_hand_open(self, hand):
        return all(angle > 150 for angle in hand["finger_curls_deg"].values())

    def is_hand_closed(self, hand):
        # return all(angle < 100 for angle in hand["finger_curls_deg"].values()) #solucion de gpt
        return not self.is_hand_open(hand)

    def is_pinch(self, hand, threshold=40):
        return hand["pinch_distance_px"] < threshold

    def is_rock_sign(self, hand):
        # ROCK = index + pinky extended, others curled
        curls = hand["finger_curls_deg"]
        return ( curls["pinky"] > 150 # and curls["index"] > 150 #Con esto se annade que el dedo indice este siempre extendido
                and curls["middle"] < 120 and curls["ring"] < 120)

    # === Main FSM logic ===
    def update(self, hands):
        print("Recibiendo en Update")
        #print(hands)
        current_time = time.time()

        # If no hands detected, always go to SENSING
        if not hands:
            if self.state != "SENSING":
                print("→ Transition to SENSING (no hands)")
            self.state = "SENSING"
            self._reset_transition()
            return self.state

        # Separate left/right hands
        left = next((h for h in hands if h["handedness"] == "Left"), None)
        if left: print(f"left>")
        right = next((h for h in hands if h["handedness"] == "Right"), None)
        if right: print(f"right>")
        #if right:
        #    print(f"isOpen > {self.is_hand_closed(right)}")

        # Determine next possible state based on conditions
        next_state = None

        if self.state == "SENSING":
            if right and self.is_rock_sign(right):
                next_state = "ZOOM"
            elif left and self.is_hand_closed(left):
                next_state = "COLOR"
            elif left and right and self.is_hand_open(left) and self.is_hand_open(right):
                next_state = "CONTROL"

        elif self.state == "ZOOM":
            if (left is not None) or (right and not self.is_rock_sign(right)):
                next_state = "SENSING"

        elif self.state == "COLOR":
            if not left or self.is_hand_open(left):
                next_state = "SENSING"

        elif self.state == "CONTROL":
            if not left or self.is_hand_closed(left):
                next_state = "SENSING"
            elif right and self.is_hand_closed(right):
                next_state = "MOVER"
            elif right and self.is_pinch(right):
                next_state = "ROTAR"

        elif self.state == "MOVER":
            if not right or not self.is_hand_closed(right):
                next_state = "CONTROL"

        elif self.state == "ROTAR":
            if not right or not self.is_pinch(right):
                next_state = "CONTROL"

        # === Handle transitions with 5s persistence ===
        if next_state and next_state != self.state:
            # Start timer if new potential transition
            if self.pending_state != next_state:
                self.pending_state = next_state
                self.condition_start = current_time
            else:
                # Check if persisted long enough
                if current_time - self.condition_start >= self.transition_delay: # type: ignore
                    print(f"→ Transition {self.state} → {next_state}")
                    self.state = next_state
                    self._reset_transition()
        else:
            self._reset_transition()

        return self.state

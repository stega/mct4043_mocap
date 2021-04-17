class Human:

  def __init__(self, width, height):
    self.frame_width  = width
    self.frame_height = height
    self.prev_rhand_x = 0
    self.prev_rhand_y = 0

  # ---------------------------------------------------------------------------
  # GET_HAND_AND_HIP_POINTS
  # sets x,y points for hips, hands, center point and hip width
  # ---------------------------------------------------------------------------
  def assign_hand_and_hip_points(self, landmarks):
    left_hip   = landmarks.landmark[24]
    right_hip  = landmarks.landmark[23]
    left_hand  = landmarks.landmark[20]
    right_hand = landmarks.landmark[19]

    # LEFT HIP
    self.lhip_x, self.lhip_y   = int(left_hip.x * self.frame_width),\
                                 int(left_hip.y * self.frame_height)
    # RIGHT HIP
    self.rhip_x, self.rhip_y   = int(right_hip.x * self.frame_width),\
                                 int(right_hip.y * self.frame_height)
    # LEFT HAND
    self.lhand_x, self.lhand_y = int(left_hand.x * self.frame_width),\
                                 int(left_hand.y * self.frame_height)
    # RIGHT HAND
    self.rhand_x, self.rhand_y = int(right_hand.x * self.frame_width),\
                                 int(right_hand.y * self.frame_height)

    # set center point
    self.center_x = int((self.lhip_x + self.rhip_x) / 2)
    self.center_y = int((self.lhip_y + self.rhip_y) / 2)

    # set hip width
    if self.rhip_x > self.lhip_x:
      self.hip_width = self.rhip_x - self.lhip_x
    else:
      self.hip_width = 200




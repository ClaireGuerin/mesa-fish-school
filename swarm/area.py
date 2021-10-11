from mesa.space import *
from swarm.vectors import *
from math import radians, pi

class SwarmSpace(ContinuousSpace):
	""" Child class of Mesa Subclass ContinuousSpace from Mesa Space
 		Overwrites get_neighbors method to include blind spot(s) """
   
	def get_neighbors(
		self, 
		pos: FloatCoordinate, 
		radius: float, 
		focal_heading: List[float],
		blind_angle: float,
		include_center: bool = True,
		include_front: bool = False
	) -> List[GridContent]:
		""" Get all objects within a certain radius.
			Works for any blind angle < pi radians (i.e. < 180 degrees)
		Args:
			pos: (x,y) coordinate tuple to center the search at.
			radius: Get all the objects within this distance of the center.
			include_center: If True, include an object at the *exact* provided
							coordinates. i.e. if you are searching for the
							neighbors of a given agent, True will include that
							agent in the results.
			focal_heading: focal.heading vector
			blind_angle: Angle of the blind spot, in degrees (will be translated to radians)
			front: If True, include blind spot in front. Else, blind spot will only be in the back
		"""
		# Neighbors are agents: 
		# 1) within radius, i.e. distance between pos and agent.pos <= radius
		# self._agent_points contains all agents positions as:
		# array([[x0, y0],
		# 		 [x1, y1],
		# 		 [x2, y2]]) etc

		deltas = np.abs( self._agent_points - np.array(pos) )

		if self.torus:
			deltas = np.minimum(deltas, self.size - deltas)
		dists = deltas[:, 0] ** 2 + deltas[:, 1] ** 2

		(idxsDist,) = np.where(dists <= radius ** 2)


		# 2) outside of blind spot (in the back, and in the front if True), i.e. 
		# IN THE BACK:
		# !(beta + Pi - alpha / 2 < gamma < beta + Pi + alpha / 2), where
		# alpha = blind_angle in radians
		# beta = heading angle of focal agent
		# gamma = angle of agent.pos from x-axis in radians

		alpha = radians(blind_angle % 360) 	# converts degrees to radians on the unit circle
											# (between 0 and 2pi)
		beta = pi2pi(angle(focal_heading))  # angle of focal direction with x+ axis
												# in radians (between 0 and 2pi)
		gamma = [pi2pi(angle( agentpos - np.array(pos) )) for agentpos in self._agent_points] 
		# angle of each agent's position with x+ axis
		# if focal pos were to be the center
		# in radians (between 0 and 2pi)

		(idxs1,) = np.where(gamma > pi2pi(beta + pi + alpha / 2))
		(idxs2,) = np.where(gamma < pi2pi(beta + pi - alpha / 2))
		idxsBack = np.intersect1d(idxs1, idxs2, assume_unique=True)

		if include_front:
			(idxs1,) = np.where(gamma > pi2pi(beta + alpha / 2))
			(idxs2,) = np.where(gamma < pi2pi(beta - alpha / 2))
			idxsFront = np.intersect1d(idxs1, idxs2, assume_unique=True)
			# Get neighbours
			intersect = np.intersect1d(np.intersect1d(idxsDist, idxsBack, assume_unique=True), idxsFront, assume_unique=True)
		else:
			# Get neighbours
			intersect = np.intersect1d(idxsDist, idxsBack, assume_unique=True)

		neighbors = [
			self._index_to_agent[x] for x in intersect if include_center or dists[x] > 0
		]

		return neighbors
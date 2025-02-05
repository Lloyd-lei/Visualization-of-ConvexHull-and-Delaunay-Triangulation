import math
from functools import cmp_to_key

class DataCloud:
    def __init__(self, points=None):
        self.points = points if points is not None else []
    
    def set_points(self, points):
        self.points = points
    
    @staticmethod
    def cross(o, a, b):
        """
        calculate orientation of triplet (o, a, b); the direction of a respective to vector{o}{b}.
                  b
                * *
              /   |
            o --* a
            o, a, b are np.array of length 2, [x, y]; x = np.array[0], y = np.array[1];
            val is the cross product of vector{pq} and vector{qr}
            return: 0: collinear; 1: clockwise, o -> a -> b turn right; counterclockwise, o -> a -> b turn left
            v1 = (a[0]-o[0], a[1]-o[1]); v2 = (b[0]-a[0], b[1]-a[1])
            v1 \cross v2 = (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        """
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    
    @staticmethod
    def dist_sq(a, b):
        """
        distance, |ab|^2
        """
        return (a[0] - b[0])**2 + (a[1] - b[1])**2
    
    def reorder_ccw(self, hull):
        """
        reorder counterclockwise: sort points on the hull by counterclockwise
          1. remove duplicate points
          2. find the most left buttom one
          3. take the pivot as the center, use arctan to implement priorityqueue
          4. let pivot be the first element
          5. implement at the tail of the stack to ensure closure
        """
        # edge case
        if len(hull) < 2:
            return hull
        if len(hull) == 2 and hull[0] != hull[-1]:
            hull.append(hull[0])
            return hull

        # if the first == last, ensure the closure
        if hull[0] == hull[-1]:
            hull = hull[:-1]
        
        # 2. take the most left buttom pivot
        pivot = min(hull, key=lambda p: (p[0], p[1]))
        
        # 3. sort all points except for pivot
        others = [p for p in hull if p != pivot]
        
        def polar_angle(p):
            # atan2(Δy, Δx) => ccw angle
            return math.atan2(p[1] - pivot[1], p[0] - pivot[0])
        
        # edge case, if two points have same ccw angle, sorted by distance
        others_sorted = sorted(
            others,
            key=lambda p: (polar_angle(p), -self.dist_sq(pivot, p))
        )
        
        # convex closure tuple [pivot] + sorted(others) + [pivot]
        final = [pivot] + others_sorted + [pivot]
        return final


    def graham_scan(self, return_steps=False):
        """
        graham scan algorithm (greedy):
            1. find the lowest far left point as the starting point; O(n)
            2. sort points in counterclockwise by orientation; O(nlogn)
            3. use recursion to iterate all point to create convex hull; O(n)
                * if right and collinear, jump out of mono stack
                * if left, jump in the mono stack
        
            if return_steps = True, return a turple containing all iteration works, for visualization
        """
        steps = []
        # steps for visualization
        if return_steps:
            steps.append(self.points.copy())

        if len(self.points) < 3:
            return [self.points.copy()] if return_steps else self.points.copy()
        
        # find the y min point, take x min if two are paralle
        pivot = min(self.points, key=lambda p: (p[1], p[0]))
        
        # sort by ccw angle; edge case: if two's ccw angles are same, sort by distance, take further one
        def compare(a, b):
            cp = self.cross(pivot, a, b)
            if cp == 0:
                return self.dist_sq(pivot, b) - self.dist_sq(pivot, a)
            return -1 if cp > 0 else 1  # cp>0 表示a在b的逆时针方向，应排在前面
        
        sorted_points = sorted([p for p in self.points if p != pivot], key=cmp_to_key(compare))
        sorted_points = [pivot] + sorted_points
        
        # stack stores convex point for visualization
        stack = []
        for p in sorted_points:
            # if the point is non left to vector{stack[0][1]}, pop out
            while len(stack) >= 2 and self.cross(stack[-2], stack[-1], p) <= 0:
                stack.pop()
                if return_steps:
                    steps.append(stack.copy())
            stack.append(p)
            if return_steps:
                steps.append(stack.copy())
        
        # convex closure
        hull = stack + [stack[0]]
        
        if return_steps:
            # store convex closure points
            for i in range(len(steps)):
                if len(steps[i]) > 1:
                    steps[i] = steps[i] + [steps[i][0]]
            steps.append(hull)
            return steps
        else:
            return hull

    def jarvis_march(self, return_steps=False):
        """
        jarvish march algorithm (greedy):
            * starting from the far left bottom point; O(n)
            * iterate and find the most counterclockwise point and
            wrap the convex with the most outer point in each step; O(nh)
               * ---- *
              /   *   |
             *  *  *  *
              \  *  * |
               *----- *
        """
        steps = []
        # stack stores convex points
        if return_steps:
            steps.append(self.points.copy())

        n = len(self.points)
        if n < 3:
            return [self.points.copy()] if return_steps else self.points.copy()
        
        hull = []
        # find the most left point as the starting
        leftmost = min(self.points, key=lambda p: p[0])
        current = leftmost
        
        while True:
            hull.append(current)
            if return_steps:
                steps.append(hull.copy())
            
            # find the next point that all next points are left to it.
            # Maybe I can use recursion to implement this?
            next_point = self.points[0]
            for p in self.points[1:]:
                cross_val = self.cross(current, next_point, p)
                # if cross<0, p is left to next point, sorted by distance if paralle
                if cross_val > 0 or (
                    cross_val == 0 and self.dist_sq(current, p) > self.dist_sq(current, next_point)):
                        next_point = p
            
            current = next_point
            if current == leftmost:
                break
        
        hull.append(hull[0]) # convex closure
        
        if return_steps:
            # ensure convex closure
            for i in range(len(steps)):
                if len(steps[i]) > 1:
                    steps[i] = steps[i] + [steps[i][0]]
            steps.append(hull)
            return steps
        else:
            return hull

    def quickhull(self, return_steps=False):
        """
        QuickHull algorithm (use pivot but more like mergeSort):
            * find the most left and most right points; O(n)
            * divide into upper convex and lower convex; O(n)
            * recursively find the farthest point in the subset; O(nlogn)
            * merge upper and lower; O(n)
            ------------------------------
                   *  <-- c
                  / \  
                 / * \ 
                / **  \ 
          a -->* ===== * <-- b   divide at the line, find c and d which are furthest points to the line
                \ * * /
                 \ * /
                  \ /
                   * <-- d
        """
        steps = []
        
        # store the starting point
        if return_steps:
            steps.append(self.points.copy())
        
        # closure condition
        if len(self.points) < 3:
            if len(self.points) == 2 and self.points[0] != self.points[1]:
                hull = self.points[:] + [self.points[0]]
            else:
                hull = self.points[:]
            if return_steps:
                return [hull]
            else:
                return hull
        
        # 1. find a = x_min, b = x_max, two extreme points
        a = min(self.points, key=lambda p: p[0])
        b = max(self.points, key=lambda p: p[0])
        
        # upper ( cross(a,b,p) > 0 ) and lower( cross(a,b,p) < 0 )
        upper = [p for p in self.points if self.cross(a, b, p) > 0]
        lower = [p for p in self.points if self.cross(a, b, p) < 0]
        
        def _hull(p1, p2, pts):
            """
            recursively find the farthest point in subsets
            """
            if not pts:
                return []
            
            # find the farthest point to vector p1->p2
            max_dist = -1
            farthest = None
            for pt in pts:
                dist = abs(self.cross(p1, p2, pt))
                if dist > max_dist:
                    max_dist = dist
                    farthest = pt
            
            # divide into two parts
            pts_left = [p for p in pts if self.cross(p1, farthest, p) > 0]
            pts_right = [p for p in pts if self.cross(farthest, p2, p) > 0]
            
            left_hull = _hull(p1, farthest, pts_left)
            right_hull = _hull(farthest, p2, pts_right)
            
            sub_hull = left_hull + [farthest] + right_hull
            
            if return_steps:
                # store steps for visualization
                if len(sub_hull) > 0:
                    # ensure convex closure
                    steps.append(sub_hull + [sub_hull[0]])
            return sub_hull
        
        # upper hull caller and lower hull caller
        upper_hull = _hull(a, b, upper)
        lower_hull = _hull(b, a, lower)
        
        # merge two hulls 
        full_hull = [a] + upper_hull + [b] + lower_hull + [a]
        
        # ccw all points
        final_hull = self.reorder_ccw(full_hull)
        
        if return_steps:
            # steps store all ccw points
            steps.append(final_hull)
            return steps
        else:
            return final_hull

    def monotone_chain(self, return_steps=False):
        """
        Monotone Chain Algorithm (greedy; PriorityQueue):
            * sort points from left to right, x_min to x_max; O(nlogn)
            * create upper hull: from left to right, sort by ccw; O(n)
            * create lower hull: from right to left, sort by ccw; O(n)
            * merge lower and upper; O(n)
            ------------------------------------
              * <-- * <-- *
             /    *    *   \     
            *     *  *      *
             \  *    *     /
              * --> * --> *

        """
        steps = []
        # store steps for visualization
        if return_steps:
            steps.append(self.points.copy())

        # PriorityQueue of x, if x paralle then append bigger y
        points = sorted(self.points, key=lambda p: (p[0], p[1]))
        if len(points) < 3:
            hull = points + [points[0]]  # ensure closure
            if return_steps:
                return [hull]
            else:
                return hull

        # create lower hull
        lower = []
        for p in points:
            while len(lower) >= 2 and self.cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
                if return_steps:
                    steps.append(lower.copy())
            lower.append(p)
            if return_steps:
                steps.append(lower.copy())
        
        # create upper hull
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and self.cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
                if return_steps:
                    steps.append(upper.copy())
            upper.append(p)
            if return_steps:
                steps.append(upper.copy())
        
        # merge two hulls
        full_hull = lower[:-1] + upper[:-1]
        hull_closed = full_hull + [full_hull[0]]
        
        if return_steps:
            # stores each steps of hull
            for i in range(len(steps)):
                if len(steps[i]) > 1:
                    steps[i] = steps[i] + [steps[i][0]]
            steps.append(hull_closed)
            return steps
        else:
            return hull_closed

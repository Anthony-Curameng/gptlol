from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QColor,QPainter,QPen,QBrush
from PySide6.QtWidgets import QWidget
from ...enums import OuterBoundaryType,SegmentType,SurfaceType
class CrossSectionWidget(QWidget):
    def __init__(self,parent=None):super().__init__(parent);self.road=None;self.result=None;self.setMinimumHeight(300)
    def set_calculation(self,road,result):self.road,self.result=road,result;self.update()
    def _side_parts(self,side,allowance):
        if side is None:return allowance,0,QColor("#4da3d9")
        excluded=max(0,side.distance_from_outer_edge_m-allowance)
        excluded_color=QColor("#8b6b3f") if side.surface_beyond_edge==SurfaceType.UNSEALED else QColor("#d8dde2")
        return allowance,excluded,excluded_color
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.RenderHint.Antialiasing);painter.fillRect(self.rect(),QColor("#f4f6f8"))
        if not self.road or not self.result:return
        left_inc,left_exc,left_color=self._side_parts(self.road.left_boundary,self.result.left_allowance_m);right_inc,right_exc,right_color=self._side_parts(self.road.right_boundary,self.result.right_allowance_m)
        diagram_width=left_exc+left_inc+self.result.internal_width_m+right_inc+right_exc; margin,y,h=45,75,105;scale=(self.width()-2*margin)/max(diagram_width,.1);x=margin
        painter.fillRect(QRectF(x,y,left_exc*scale,h),left_color);x+=left_exc*scale;painter.fillRect(QRectF(x,y,left_inc*scale,h),QColor("#4da3d9"));x+=left_inc*scale;left_edge=x
        if self.result.included_segments:
            for segment in self.result.included_segments:
                width=segment.total_width_m*scale;color=QColor("#d5a900") if segment.segment_type==SegmentType.INTERNAL_PAINTED_SEPARATION else QColor("#414b53");brush=QBrush(color,Qt.BrushStyle.BDiagPattern if segment.segment_type==SegmentType.INTERNAL_PAINTED_SEPARATION else Qt.BrushStyle.SolidPattern);painter.fillRect(QRectF(x,y,width,h),brush);painter.setPen(QColor("white"));painter.drawText(QRectF(x,y,width,h),Qt.AlignmentFlag.AlignCenter|Qt.TextFlag.TextWordWrap,f"{segment.label}\n{segment.total_width_m:.2f} m");x+=width
        else:painter.fillRect(QRectF(x,y,self.result.internal_width_m*scale,h),QColor("#414b53"));painter.setPen(QColor("white"));painter.drawText(QRectF(x,y,self.result.internal_width_m*scale,h),Qt.AlignmentFlag.AlignCenter,f"Internal span\n{self.result.internal_width_m:.2f} m");x+=self.result.internal_width_m*scale
        right_edge=x;painter.fillRect(QRectF(x,y,right_inc*scale,h),QColor("#4da3d9"));x+=right_inc*scale;painter.fillRect(QRectF(x,y,right_exc*scale,h),right_color);x+=right_exc*scale
        edge_pen=QPen(QColor("white"),3,Qt.PenStyle.DashLine);painter.setPen(edge_pen);painter.drawLine(left_edge,y-5,left_edge,y+h+5);painter.drawLine(right_edge,y-5,right_edge,y+h+5)
        kerb_pen=QPen(QColor("black"),6);painter.setPen(kerb_pen)
        if self.road.left_boundary and self.road.left_boundary.outer_boundary==OuterBoundaryType.KERB:painter.drawLine(margin,y-10,margin,y+h+10)
        if self.road.right_boundary and self.road.right_boundary.outer_boundary==OuterBoundaryType.KERB:painter.drawLine(x,y-10,x,y+h+10)
        final_start=left_edge-self.result.left_allowance_m*scale;painter.setPen(QPen(QColor("#c62828"),3));painter.drawLine(final_start,y+h+35,final_start+self.result.final_wk_m*scale,y+h+35);painter.drawText(QRectF(final_start,y+h+38,self.result.final_wk_m*scale,25),Qt.AlignmentFlag.AlignCenter,f"Final Wk = {self.result.final_wk_m:.2f} m")
        painter.setPen(QColor("#17212b"));painter.drawText(QRectF(margin,10,self.width()-2*margin,45),Qt.AlignmentFlag.AlignCenter,"Outer traffic-edge line — not a centre line or lane-divider line.\nDark grey: vehicle/internal • yellow hatch: painted internal • blue: included seal • pale grey/brown: excluded")
        painter.drawText(QRectF(margin,self.height()-24,self.width()-2*margin,20),Qt.AlignmentFlag.AlignCenter,"Diagrammatic only — entered dimensions govern.")

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsSimpleTextItem, QGraphicsView
from wkcalc.calculator import WkResult
from wkcalc.enums import BoundaryType
from wkcalc.models import RoadInput, TravelledElement

class CrossSectionView(QGraphicsView):
    def __init__(self,parent=None):
        super().__init__(parent); self.setMinimumHeight(300); self.setRenderHints(self.renderHints()); self.setScene(QGraphicsScene(self)); self.setBackgroundBrush(QColor("#f4f7fa"))
    def draw_geometry(self, road: RoadInput, result: WkResult, elements: list[TravelledElement]):
        scene=self.scene(); scene.clear(); x,y,height=50.0,90.0,95.0; scale=700/max(result.unrestricted_wk_m,1)
        sections=[("Left allowance",result.left.allowance_m,QColor("#9dc9e2")),("Travelled way",road.travelled_width_m,QColor("#465866")),("Right allowance",result.right.allowance_m,QColor("#9dc9e2"))]
        positions=[]
        for label,width,color in sections:
            pixels=width*scale; scene.addRect(x,y,pixels,height,QPen(Qt.PenStyle.NoPen),QBrush(color)); text=scene.addSimpleText(f"{label}\n{width:.2f} m"); text.setBrush(QColor("white") if label=="Travelled way" else QColor("#17212b")); text.setPos(x+max(4,pixels/2-text.boundingRect().width()/2),y+28); positions.append((x,pixels)); x+=pixels
        left_edge=positions[1][0]; right_edge=left_edge+positions[1][1]
        edge_pen=QPen(QColor("white"),2,Qt.PenStyle.DashLine); scene.addLine(left_edge,y,left_edge,y+height,edge_pen); scene.addLine(right_edge,y,right_edge,y+height,edge_pen)
        kerb_pen=QPen(QColor("#17212b"),5)
        if road.left.boundary_type in {BoundaryType.KERB_AT_TRAVELLED_EDGE,BoundaryType.KERB_BEYOND_EDGE_LINE}: scene.addLine(positions[0][0],y-10,positions[0][0],y+height+10,kerb_pen)
        if road.right.boundary_type in {BoundaryType.KERB_AT_TRAVELLED_EDGE,BoundaryType.KERB_BEYOND_EDGE_LINE}: scene.addLine(x,y-10,x,y+height+10,kerb_pen)
        wk_pen=QPen(QColor("#c62828"),3); final_pixels=result.final_wk_m*scale; scene.addLine(50,y+height+45,50+final_pixels,y+height+45,wk_pen); label=scene.addSimpleText(f"Wk = {result.final_wk_m:.2f} m"); label.setBrush(QColor("#c62828")); label.setPos(50+final_pixels/2-label.boundingRect().width()/2,y+height+50)
        if elements:
            element_text="  |  ".join(f"{e.quantity} × {e.element_type} @ {e.individual_width:.2f} m" for e in elements if e.included); item=scene.addSimpleText(element_text); item.setPos(left_edge,y-30)
        scene.setSceneRect(scene.itemsBoundingRect().adjusted(-30,-30,30,30)); self.fitInView(scene.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if not self.scene().sceneRect().isEmpty(): self.fitInView(self.scene().sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
